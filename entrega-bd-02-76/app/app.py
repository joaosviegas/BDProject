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
import random
import random
import psycopg

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

# --------------------------- / ----------------------------
@app.route("/", methods=("GET",))
@limiter.limit("1 per second")
def aeroporto_index():
    """ Lista todos os aeroportos (nome e cidade). """

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

# -------------------- /voos/<partida> ---------------------
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

            # Verifica se o aeroporto de partida existe
            cur.execute(
                """
                SELECT nome FROM aeroporto WHERE codigo = %(partida)s;
                """,
                {"partida": partida},
            )

            # Se o aeroporto não existir, retorna 404
            if cur.rowcount == 0:
                log.error(f"Aeroporto {partida} não encontrado.")
                return jsonify({"message": f"Aeroporto {partida} não encontrado.", "status": "error"}), 404
            
            # Se o aeroporto existe
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

# -------------- /voos/<partida>/<chegada> -----------------
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
            # Verifica se os aeroportos de partida e chegada existem
            cur.execute(
                """
                SELECT codigo, cidade FROM aeroporto WHERE codigo = %(partida)s OR codigo = %(chegada)s;
                """,
                {"partida": partida, "chegada": chegada},
            )
            
            # Junta os codigos com as cidades
            aeroportos_cidades = {}
            for row in cur.fetchall():
                aeroportos_cidades[row.codigo] = row.cidade

            # Se pelo menos um dos aeroportos não existir
            if cur.rowcount < 2:
                log.error(f"Aeroporto(s) {partida} ou {chegada} não encontrado(s).")
                return jsonify({"message": f"Aeroporto(s) {partida} ou {chegada} não encontrado(s).", "status": "error"}), 404

            # Se forem da mesma cidade, não há voos
            if aeroportos_cidades[partida] == aeroportos_cidades[chegada]:
                log.error(f"Aeroportos de {partida} e {chegada} estão na mesma cidade ({aeroportos_cidades[partida]}), não há voos entre aeroportos da mesma cidade.")
                return jsonify({
                    "message": f"Aeroportos de {partida} e {chegada} estão na mesma cidade ({aeroportos_cidades[partida]}). Não há voos entre aeroportos da mesma cidade.", 
                    "status": "error"
                }), 400
            
            # Se existirem mas forem da mesma ciade, não existem voos, 400 Bad Request
            if partida == chegada:
                log.error(f"Partida e chegada são o mesmo aeroporto: {partida}.")
                return jsonify({"message": f"Partida e chegada são o mesmo aeroporto: {partida}.", "status": "error"}), 400
            
            # Se os aeroportos existem, busca os voos disponíveis
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

def calcula_preco_bilhete(prim_classe, voo):
    """
    Função Auxiliar que calcula o preço do bilhete tendo em conta a classe do bilhete.
    """

    # Obtem o aeroporto de partida e chegada do voo
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT partida, chegada
                FROM voo
                WHERE id = %(voo_id)s;
                """,
                {"voo_id": voo}
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Voo não encontrado.")
            partida, chegada = row.partida, row.chegada

    if prim_classe:
        return random.randint(450, 825)
    else:
        return random.randint(60, 380)
        

# --------------------- /compra/<voo>/ ---------------------
@app.route("/compra/<voo>/", methods=("POST",))
@limiter.limit("1 per second")
def compra_voo(voo):
    """
    Faz uma compra de um ou mais bilhetes para o <voo>,
    populando as tabelas <venda> e <bilhete>. Recebe como
    argumentos o nif do cliente, e uma lista de pares (nome de
    passageiro, classe de bilhete) especificando os bilhetes a
    comprar.

    Exemplo de JSON esperado:
    {
        "nif": "123456789",
        "bilhetes": [
            {"nome": "João Silva", "classe": true},
            {"nome": "Maria Santos", "classe": false}
        ]
    }

    """

    bilhetes = []
    # Se for JSON
    if request.is_json:
        data = request.get_json()
        nif = data.get("nif")
        

        if "bilhetes" in data:
            for b in data["bilhetes"]:
                bilhetes.append({
                    "nome": b.get("nome"),
                    "classe": b.get("classe", False)
                })

    else:
        # Se não for JSON, extrair os dados dos parâmetros da query string
        nif = request.args.get("nif")
        nomes = request.args.getlist("nome")
        classes = request.args.getlist("classe")
  
        for nome, classe in zip(nomes, classes):
            bilhetes.append({
                "nome": nome,
                "classe": True if (classe.lower() == "true" or classe.lower() == "t") else False
            })

    if not nif or not bilhetes:
        return jsonify({"message": "NIF e bilhetes são obrigatórios.", "status": "error"}), 400

    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                with conn.transaction():

                    # 0. Lock the venda table to prevent concurrent modifications and inconsistencies (sell more tickets than available)
                    cur.execute("LOCK TABLE venda IN EXCLUSIVE MODE;")

                    # 1. Inserir venda
                    cur.execute(
                        """
                        INSERT INTO venda (nif_cliente, balcao, hora)
                        VALUES (%s, %s, NOW())
                        RETURNING codigo_reserva;
                        """,
                        (nif, None) # Venda online, balcão é NULL
                    )
                    codigo_reserva = cur.fetchone().codigo_reserva

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
                                calcula_preco_bilhete(b["classe"], voo),
                                b["classe"],
                                None,      # lugar fica NULL, atribuído no check-in
                                None   # no_serie a NULL, atribuido no check-in
                            )
                        )
                        bilhete_ids.append(cur.fetchone().id)

            except psycopg.Error as e:
                
                # Erro de venda depois da partida
                if e.sqlstate == 'P0001':
                    log.error(f"Erro ao reservar bilhetes: {str(e).split("\n")[0]}")
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 400

                # Erro de capacidade esgotada
                elif e.sqlstate == 'P0002':
                    log.error(f"Erro ao reservar bilhetes: {str(e).split("\n")[0]}")
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 400

            except Exception as e:
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 500

    return jsonify({"codigo_reserva": codigo_reserva, "bilhete_ids": bilhete_ids}), 201


# ------------------ /checkin/<bilhete> --------------------
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
                    cur.execute(
                        """
                        SELECT id, lugar
                        FROM bilhete
                        WHERE id = %(bilhete_id)s;
                        """,
                        {"bilhete_id": bilhete},
                    )
                    ticket_exists = cur.fetchone()

                    #1. Verificar se o bilhete existe
                    if not ticket_exists:
                        return jsonify({"message": "Bilhete não encontrado.", "status": "error"}), 404

                    # 2. Verificar se já fez o checkin (lugar atribuido)
                    if ticket_exists.lugar is not None:
                        return jsonify({"message": "Este bilhete já fez o check-in.", "status": "error"}), 400
                    
                    # 3. Buscar info do bilhete
                    cur.execute(
                        """
                        SELECT b.voo_id, b.prim_classe, v.no_serie
                        FROM bilhete b
                        JOIN voo v ON v.id = b.voo_id
                        WHERE b.id = %(bilhete_id)s AND b.lugar IS NULL;
                        """,
                        {"bilhete_id": bilhete},
                    )
                    bilhete_row = cur.fetchone()
                    voo_id = bilhete_row.voo_id
                    prim_classe = bool(bilhete_row.prim_classe)
                    no_serie = bilhete_row.no_serie

                    # 4. Procurar um lugar disponível da classe correta (e dá FOR UPDATE para não que ninguém mais possa ter o mesmo lugar)
                    cur.execute(
                        """
                        SELECT a.lugar
                        FROM assento a
                        WHERE a.no_serie = %(no_serie)s
                          AND a.prim_classe = %(prim_classe)s
                          AND NOT EXISTS (
                            SELECT 1
                            FROM bilhete b
                            WHERE b.lugar = a.lugar
                              AND b.no_serie = a.no_serie
                              AND b.voo_id = %(voo_id)s
                          )
                        FOR UPDATE
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
                        return jsonify({"message": "Nenhum lugar disponível na classe selecionada.", "status": "error"}), 404
                    lugar = lugar_row.lugar

                    # 5. Atualizar o bilhete com o lugar
                    cur.execute(
                        """
                        UPDATE bilhete
                        SET lugar = %(lugar)s, no_serie = %(no_serie)s
                        WHERE id = %(bilhete_id)s;
                        """,
                        {
                         "lugar": lugar,
                         "bilhete_id": bilhete,
                         "no_serie": no_serie
                         },
                    )
                    log.debug(f"Check-in realizado com sucesso para o bilhete {bilhete}, lugar {lugar}.")

            except psycopg.Error as e:
                conn.rollback()
                # Avião do assento não corresponde    
                if e.sqlstate == 'P0003':
                    log.error(f"Erro no check-in: {str(e).split("\n")[0]}")
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 400
                
                # Erro de Assento não existe no avião
                elif e.sqlstate == 'P0004':
                    log.error(f"Erro no check-in: {str(e).split("\n")[0]}")
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 404
                
                # Erro de classe não correspondente
                elif e.sqlstate == 'P0005':
                    log.error(f"Erro no check-in: {str(e).split("\n")[0]}")
                    return jsonify({"message": str(e).split("\n")[0], "status": "error"}), 400

            except Exception as e:
                conn.rollback()
                log.error(f"Erro inesperado: {str(e).split("\n")[0]}")
                return jsonify({"message": f"Ocorreu um erro: {str(e).split("\n")[0]}", "status": "error"}), 500

    return jsonify({"message": "Check-in realizado com sucesso.", "lugar": lugar}), 200

if __name__ == "__main__":
    app.run()