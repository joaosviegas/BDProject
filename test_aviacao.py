import pytest
import psycopg2
from datetime import datetime, timedelta

@pytest.fixture
def db_connection():
    """Fixture para conexão com a base de dados"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="aviacao",
        user="postgres",
        password="postgres"
    )
    yield conn
    conn.close()

def test_ri_1_check_existing_data(db_connection):
    """Teste: Verificar se RI-1 está ativa nos dados existentes"""
    cur = db_connection.cursor()
    
    # Verificar se existem violações de RI-1 nos dados existentes
    cur.execute("""
        SELECT COUNT(*) FROM bilhete b
        JOIN voo v ON b.voo_id = v.id
        WHERE b.lugar IS NOT NULL 
          AND b.no_serie IS NOT NULL 
          AND (b.no_serie != v.no_serie 
               OR b.prim_classe != (
                   SELECT prim_classe FROM assento 
                   WHERE lugar = b.lugar AND no_serie = b.no_serie
               ))
    """)
    violations = cur.fetchone()[0]
    assert violations == 0, f"Encontradas {violations} violações de RI-1 nos dados existentes"

def test_ri_1_invalid_airplane_update(db_connection):
    """Teste: RI-1 - Tentar atualizar bilhete com avião incorreto"""
    cur = db_connection.cursor()
    
    # Encontrar um bilhete com check-in feito
    cur.execute("""
        SELECT b.id, b.no_serie, v.no_serie as voo_aviao 
        FROM bilhete b 
        JOIN voo v ON b.voo_id = v.id 
        WHERE b.lugar IS NOT NULL 
        LIMIT 1
    """)
    result = cur.fetchone()
    
    if result:
        bilhete_id, bilhete_aviao, voo_aviao = result
        
        # Tentar trocar para avião diferente (deve falhar)
        try:
            cur.execute("""
                UPDATE bilhete 
                SET no_serie = 'AVIAO_INEXISTENTE' 
                WHERE id = %s
            """, (bilhete_id,))
            db_connection.commit()
            assert False, "RI-1 deveria ter impedido a atualização"
        except psycopg2.errors.RaiseException as e:
            print(f"✅ RI-1 funcionou: {str(e)[:50]}...")
            db_connection.rollback()

def test_ri_2_capacity_check(db_connection):
    """Teste: RI-2 - Verificar se capacidades estão sendo respeitadas"""
    cur = db_connection.cursor()
    
    # Verificar se algum voo excede a capacidade
    cur.execute("""
        SELECT 
            v.id,
            COUNT(*) FILTER (WHERE b.prim_classe = TRUE) as bilhetes_1c,
            COUNT(*) FILTER (WHERE b.prim_classe = FALSE) as bilhetes_2c,
            (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = TRUE) as capacidade_1c,
            (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = FALSE) as capacidade_2c
        FROM voo v
        LEFT JOIN bilhete b ON v.id = b.voo_id
        GROUP BY v.id, v.no_serie
        HAVING COUNT(*) FILTER (WHERE b.prim_classe = TRUE) > 
               (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = TRUE)
            OR COUNT(*) FILTER (WHERE b.prim_classe = FALSE) > 
               (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = FALSE)
    """)
    
    violations = cur.fetchall()
    assert len(violations) == 0, f"Encontrados {len(violations)} voos com capacidade excedida"

def test_ri_2_try_exceed_capacity(db_connection):
    """Teste: RI-2 - Tentar exceder capacidade"""
    cur = db_connection.cursor()
    
    # Encontrar um voo próximo da capacidade máxima
    cur.execute("""
        SELECT 
            v.id,
            COUNT(*) FILTER (WHERE b.prim_classe = TRUE) as bilhetes_1c,
            (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = TRUE) as capacidade_1c
        FROM voo v
        LEFT JOIN bilhete b ON v.id = b.voo_id
        GROUP BY v.id, v.no_serie
        HAVING COUNT(*) FILTER (WHERE b.prim_classe = TRUE) < 
               (SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = TRUE)
        ORDER BY ((SELECT COUNT(*) FROM assento WHERE no_serie = v.no_serie AND prim_classe = TRUE) - COUNT(*) FILTER (WHERE b.prim_classe = TRUE)) ASC
        LIMIT 1
    """)
    
    result = cur.fetchone()
    if result:
        voo_id, bilhetes_1c, capacidade_1c = result
        
        # Criar uma venda
        cur.execute("""
            INSERT INTO venda (nif_cliente, balcao, hora) 
            VALUES ('999999999', 'LIS', '2024-01-01 10:00')
            RETURNING codigo_reserva
        """)
        venda_id = cur.fetchone()[0]
        
        # Tentar vender bilhetes até exceder capacidade
        tickets_to_add = capacidade_1c - bilhetes_1c + 1  # +1 para exceder
        
        for i in range(tickets_to_add):
            try:
                cur.execute("""
                    INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe) 
                    VALUES (%s, %s, %s, 100.00, TRUE)
                """, (voo_id, venda_id, f'Teste Capacidade {i}'))
                
                if i == tickets_to_add - 1:  # Último bilhete deve falhar
                    db_connection.commit()
                    assert False, "RI-2 deveria ter impedido exceder a capacidade"
            except psycopg2.errors.RaiseException as e:
                print(f"✅ RI-2 funcionou: {str(e)[:50]}...")
                db_connection.rollback()
                break

def test_ri_3_sale_time_check(db_connection):
    """Teste: RI-3 - Verificar se vendas são anteriores aos voos"""
    cur = db_connection.cursor()
    
    # Verificar se existem violações nos dados
    cur.execute("""
        SELECT COUNT(*) FROM bilhete b
        JOIN venda s ON b.codigo_reserva = s.codigo_reserva
        JOIN voo v ON b.voo_id = v.id
        WHERE s.hora >= v.hora_partida
    """)
    violations = cur.fetchone()[0]
    assert violations == 0, f"Encontradas {violations} violações de RI-3 nos dados existentes"

def test_ri_3_try_late_sale(db_connection):
    """Teste: RI-3 - Tentar fazer venda após partida"""
    cur = db_connection.cursor()
    
    # Encontrar um voo futuro
    cur.execute("""
        SELECT id, hora_partida FROM voo 
        WHERE hora_partida > NOW() 
        LIMIT 1
    """)
    result = cur.fetchone()
    
    if result:
        voo_id, hora_partida = result
        
        # Criar venda após a partida
        try:
            cur.execute("""
                INSERT INTO venda (nif_cliente, balcao, hora) 
                VALUES ('888888888', 'LIS', %s)
                RETURNING codigo_reserva
            """, (hora_partida + timedelta(hours=1),))
            venda_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe) 
                VALUES (%s, %s, 'Teste Tardio', 100.00, FALSE)
            """, (voo_id, venda_id))
            
            db_connection.commit()
            assert False, "RI-3 deveria ter impedido a venda tardia"
        except psycopg2.errors.RaiseException as e:
            print(f"✅ RI-3 funcionou: {str(e)[:50]}...")
            db_connection.rollback()

def test_database_requirements(db_connection):
    """Teste: Verificar se os requisitos da base de dados são cumpridos"""
    cur = db_connection.cursor()
    
    # Verificar aeroportos
    cur.execute("SELECT COUNT(*) FROM aeroporto")
    airports_count = cur.fetchone()[0]
    assert airports_count >= 10, f"Apenas {airports_count} aeroportos (requer ≥10)"
    
    # Verificar aviões
    cur.execute("SELECT COUNT(*) FROM aviao")
    planes_count = cur.fetchone()[0]
    assert planes_count >= 10, f"Apenas {planes_count} aviões (requer ≥10)"
    
    # Verificar modelos
    cur.execute("SELECT COUNT(DISTINCT modelo) FROM aviao")
    models_count = cur.fetchone()[0]
    assert models_count >= 3, f"Apenas {models_count} modelos (requer ≥3)"
    
    # Verificar vendas
    cur.execute("SELECT COUNT(*) FROM venda")
    sales_count = cur.fetchone()[0]
    assert sales_count >= 10000, f"Apenas {sales_count} vendas (requer ≥10,000)"
    
    # Verificar bilhetes
    cur.execute("SELECT COUNT(*) FROM bilhete")
    tickets_count = cur.fetchone()[0]
    assert tickets_count >= 30000, f"Apenas {tickets_count} bilhetes (requer ≥30,000)"
    
    print(f"✅ Todos os requisitos cumpridos:")
    print(f"   📍 Aeroportos: {airports_count}")
    print(f"   ✈️  Aviões: {planes_count}")
    print(f"   🔧 Modelos: {models_count}")
    print(f"   🎫 Vendas: {sales_count}")
    print(f"   🎟️  Bilhetes: {tickets_count}")