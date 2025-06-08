#!/usr/bin/python3
# Copyright (c) BDist Development Team
# Distributed under the terms of the Modified BSD License.
import os
from logging.config import dictConfig

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from psycopg.rows import namedtuple_row
from psycopg_pool import ConnectionPool

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s:%(lineno)s - %(funcName)20s(): %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")

app = Flask(__name__)
app.config.from_prefixed_env()
log = app.logger
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=RATELIMIT_STORAGE_URI,
)

# Use the DATABASE_URL environment variable if it exists, otherwise use the default.
# Use the format postgres://username:password@hostname/database_name to connect to the database.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://postgres:postgres@postgres/aviacao")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={
        "autocommit": True,  # If True don’t start transactions automatically.
        "row_factory": namedtuple_row,
    },
    min_size=4,
    max_size=10,
    open=True,
    # check=ConnectionPool.check_connection,
    name="postgres_pool",
    timeout=5,
)


def is_decimal(s):
    """Returns True if string is a parseable float number."""
    try:
        float(s)
        return True
    except ValueError:
        return False

# /
@app.route("/", methods=("GET",))
@limiter.limit("1 per second")
def aeroporto_index():
    """Show all airports."""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            aeroportos = cur.execute(
                """
                SELECT nome, cidade FROM aeroporto;
                """,
                {},
            ).fetchall()
            log.debug(f"Found {cur.rowcount} airports.")

    return jsonify(aeroportos), 200

# /voos/<partida>
@app.route("/voos/<partida>/", methods=("GET",))
@limiter.limit("1 per second")
def voos_por_partida(partida):
    """
    Lista todos os voos (número de série do avião, hora de partida
    e aeroporto de chegada) que partem do aeroporto de <partida>
    até 12h após o momento da consulta.
    """
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            voos = cur.execute(
                """
                SELECT no_serie, hora_partida, chegada 
                FROM voo 
                WHERE partida = %(partida)s
                AND hora_partida >= NOW()
                AND hora_partida <= Now() + INTERVAL '12 hours'
                ORDER BY hora_partida;
                """,
                {   
                    "partida": partida,
                },
            ).fetchall()
            log.debug(f"Found {cur.rowcount} flights departing from {partida} in the next 12 hours.")
    
    return jsonify(voos), 200

# /voos/<partida>/<chegada>
@app.route("/voos/<partida>/<chegada>", methods=("GET",))
@limiter.limit("1 per second")
def voos_por_partida_chegada(partida, chegada):
    """
    Lista os próximos três voos (número de série do avião e hora
    de partida) entre o aeroporto de <partida> e o aeroporto
    de <chegada> para os quais ainda há bilhetes disponíveis.
    """
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            voos = cur.execute(
                """
                SELECT v.no_serie, v.hora_partida
                FROM voo v
                JOIN assento a ON a.no_serie = v.no_serie
                LEFT JOIN bilhete b ON b.voo_id = v.id AND b.lugar = a.lugar AND b.no_serie = a.no_serie
                WHERE v.partida = %(partida)s
                AND v.chegada = %(chegada)s
                AND v.hora_partida > NOW()
                AND b.id IS NULL  -- lugar ainda não reservado
                GROUP BY v.id, v.no_serie, v.hora_partida
                ORDER BY v.hora_partida
                LIMIT 3;

                """,
                {
                    "partida": partida,
                    "chegada": chegada,
                },
            ).fetchall()
            log.debug(f"Found {cur.rowcount} flights from {partida} to {chegada} with seats available.")
    
    return jsonify(voos), 200

# TODO
# /compra/<voo>/
@app.route("/compra/<voo>/", methods=("POST",))
@limiter.limit("1 per second")
def compra_voo(voo):
    """
    Faz uma compra de um ou mais bilhetes para o <voo>,
    populando as tabelas <venda> e <bilhete>. Recebe como
    argumentos o nif do cliente, e uma lista de pares (nome de
    passageiro, classe de bilhete) especificando os bilhetes a
    comprar.
    """
    data = request.get_json()
    nif = data.get("nif")
    bilhetes = data.get("bilhetes", [])

    if not nif or not bilhetes:
        return jsonify({"message": "NIF e bilhetes são obrigatórios.", "status": "error"}), 400

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():
                    # 1. Inserir venda
                    cur.execute(
                        """
                        INSERT INTO venda (nif_cliente, balcao, hora)
                        VALUES (%s, %s, NOW())
                        RETURNING codigo_reserva;
                        """,
                        (nif, "LIS")
                    )
                    codigo_reserva = cur.fetchone().codigo_reserva

                    # 2. Obter o no_serie do voo
                    cur.execute(
                        "SELECT no_serie FROM voo WHERE id = %s;",
                        (voo,)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise Exception("Voo não encontrado.")
                    no_serie = row.no_serie

                    bilhete_ids = []
                    for b in bilhetes:
                        cur.execute(
                            """
                            INSERT INTO bilhete (
                                voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, lugar, no_serie
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                            """,
                            (
                                voo,
                                codigo_reserva,
                                b["nome"],
                                100,  # ou calcula o preço
                                b["prim_classe"],
                                None,      # lugar fica NULL
                                no_serie   # no_serie correto do voo
                            )
                        )
                        bilhete_ids.append(cur.fetchone().id)
            except Exception as e:
                return jsonify({"message": str(e), "status": "error"}), 500

    return jsonify({"codigo_reserva": codigo_reserva, "bilhete_ids": bilhete_ids}), 201

# TODO
# /checkin/<bilhete>
@app.route("/checkin/<bilhete>/", methods=("PUT",))
@limiter.limit("1 per second")
def checkin(bilhete):
    """
    Faz o check-in de um bilhete, atribuindo-lhe automaticamente
    um assento da classe correspondente.
    """
    
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():
                    # BEGIN is executed, a transaction started
                    cur.execute(
                        """
                        UPDATE bilhete
                        SET utilizado = TRUE
                        WHERE id = %(bilhete_id)s;
                        """,
                        {"bilhete_id": bilhete},
                    )
                    log.debug(f"Bilhete {bilhete} marcado como utilizado.")
            except Exception as e:
                return jsonify({"message": str(e), "status": "error"}), 500
            else:
                # COMMIT is executed at the end of the block.
                # The connection is in idle state again.
                log.debug(f"Check-in realizado com sucesso para o bilhete {bilhete}.")
    
    return jsonify({"message": "Check-in realizado com sucesso."}), 200



#------------- Codigo do LAB10 ----------------------------



@app.route("/accounts", methods=("GET",))
@limiter.limit("1 per second")
def account_index():
    """Show all the accounts, most recent first."""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            accounts = cur.execute(
                """
                SELECT account_number, branch_name, balance
                FROM account
                ORDER BY account_number DESC;
                """,
                {},
            ).fetchall()
            log.debug(f"Found {cur.rowcount} rows.")

    return jsonify(accounts), 200


@app.route("/accounts/<account_number>/update", methods=("GET",))
@limiter.limit("1 per second")
def account_update_view(account_number):
    """Show the page to update the account balance."""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            account = cur.execute(
                """
                SELECT account_number, branch_name, balance
                FROM account
                WHERE account_number = %(account_number)s;
                """,
                {"account_number": account_number},
            ).fetchone()
            log.debug(f"Found {cur.rowcount} rows.")

    # At the end of the `connection()` context, the transaction is committed
    # or rolled back, and the connection returned to the pool.

    if account is None:
        return jsonify({"message": "Account not found.", "status": "error"}), 404

    return jsonify(account), 200


@app.route(
    "/accounts/<account_number>/update",
    methods=(
        "PUT",
        "POST",
    ),
)
def account_update_save(account_number):
    """Update the account balance."""

    balance = request.args.get("balance")

    error = None

    if not balance:
        error = "Balance is required."
    if not is_decimal(balance):
        error = "Balance is required to be decimal."

    if error is not None:
        return jsonify({"message": error, "status": "error"}), 400
    else:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE account
                    SET balance = %(balance)s
                    WHERE account_number = %(account_number)s;
                    """,
                    {"account_number": account_number, "balance": balance},
                )
                # The result of this statement is persisted immediately by the database
                # because the connection is in autocommit mode.
                log.debug(f"Updated {cur.rowcount} rows.")

                if cur.rowcount == 0:
                    return (
                        jsonify({"message": "Account not found.", "status": "error"}),
                        404,
                    )

        # The connection is returned to the pool at the end of the `connection()` context but,
        # because it is not in a transaction state, no COMMIT is executed.

        return "", 204


@app.route(
    "/accounts/<account_number>/delete",
    methods=(
        "DELETE",
        "POST",
    ),
)
def account_delete(account_number):
    """Delete the account."""

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():
                    # BEGIN is executed, a transaction started
                    cur.execute(
                        """
                        DELETE FROM depositor
                        WHERE account_number = %(account_number)s;
                        """,
                        {"account_number": account_number},
                    )
                    cur.execute(
                        """
                        DELETE FROM account
                        WHERE account_number = %(account_number)s;
                        """,
                        {"account_number": account_number},
                    )
                    # These two operations run atomically in the same transaction
            except Exception as e:
                return jsonify({"message": str(e), "status": "error"}), 500
            else:
                # COMMIT is executed at the end of the block.
                # The connection is in idle state again.
                log.debug(f"Deleted {cur.rowcount} rows.")

                if cur.rowcount == 0:
                    return (
                        jsonify({"message": "Account not found.", "status": "error"}),
                        404,
                    )

    # The connection is returned to the pool at the end of the `connection()` context

    return "", 204


@app.route("/ping", methods=("GET",))
@limiter.exempt
def ping():
    log.debug("ping!")
    return jsonify({"message": "pong!", "status": "success"})


if __name__ == "__main__":
    app.run()
