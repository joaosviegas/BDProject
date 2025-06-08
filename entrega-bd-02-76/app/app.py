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
                    # 1. Buscar info do bilhete
                    cur.execute(
                        """
                        SELECT b.voo_id, b.prim_classe, b.no_serie
                        FROM bilhete b
                        WHERE b.id = %(bilhete_id)s AND b.lugar IS NULL;
                        """,
                        {"bilhete_id": bilhete},
                    )
                    bilhete_row = cur.fetchone()
                    if not bilhete_row:
                        return jsonify({"message": "Bilhete não encontrado ou já tem lugar atribuído.", "status": "error"}), 404

                    voo_id = bilhete_row.voo_id
                    prim_classe = bool(bilhete_row.prim_classe)
                    no_serie = bilhete_row.no_serie

                    # 2. Procurar um lugar disponível da classe correta
                    cur.execute(
                        """
                        SELECT a.lugar
                        FROM assento a
                        WHERE a.no_serie = %(no_serie)s
                          AND a.prim_classe = %(prim_classe)s
                          AND a.lugar NOT IN (
                              SELECT b.lugar
                              FROM bilhete b
                              WHERE b.voo_id = %(voo_id)s AND b.no_serie = %(no_serie)s AND b.lugar IS NOT NULL
                          )
                        LIMIT 1;
                        """,
                        {
                            "no_serie": no_serie,
                            "prim_classe": prim_classe,
                            "voo_id": voo_id,
                        },
                    )
                    lugar_row = cur.fetchone()
                    if not lugar_row:
                        return jsonify({"message": "Não há lugares disponíveis nesta classe para este voo.", "status": "error"}), 409

                    lugar = lugar_row.lugar

                    # 3. Atualizar o bilhete com o lugar
                    cur.execute(
                        """
                        UPDATE bilhete
                        SET lugar = %(lugar)s
                        WHERE id = %(bilhete_id)s;
                        """,
                        {"lugar": lugar, "bilhete_id": bilhete},
                    )
                    log.debug(f"Check-in realizado com sucesso para o bilhete {bilhete}, lugar {lugar}.")
            except Exception as e:
                return jsonify({"message": str(e), "status": "error"}), 500

    return jsonify({"message": "Check-in realizado com sucesso.", "lugar": lugar}), 200

if __name__ == "__main__":
    app.run()
