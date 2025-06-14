import datetime
import random
import math

def gerar_voos_2024_2025():
    # Definições comuns
    avioes = [
        {"no_serie": "A320-001", "modelo": "Airbus A320"},
        {"no_serie": "A320-002", "modelo": "Airbus A320"},
        {"no_serie": "A320-003", "modelo": "Airbus A320"},
        {"no_serie": "A320-004", "modelo": "Airbus A320"},
        {"no_serie": "A320-005", "modelo": "Airbus A320"},
        {"no_serie": "B737-001", "modelo": "Boeing 737"},
        {"no_serie": "B737-002", "modelo": "Boeing 737"},
        {"no_serie": "B737-003", "modelo": "Boeing 737"},
        {"no_serie": "B737-004", "modelo": "Boeing 737"},
        {"no_serie": "B737-005", "modelo": "Boeing 737"},
        {"no_serie": "B787-001", "modelo": "Boeing 787"},
        {"no_serie": "B787-002", "modelo": "Boeing 787"}
    ]

    aeroportos = [
        {"codigo": "LIS", "nome": "Humberto Delgado Airport", "cidade": "Lisboa", "pais": "Portugal"},
        {"codigo": "OPO", "nome": "Francisco Sá Carneiro Airport", "cidade": "Porto", "pais": "Portugal"},
        {"codigo": "FAO", "nome": "Faro Airport", "cidade": "Faro", "pais": "Portugal"},
        {"codigo": "BJZ", "nome": "Badajoz Airport", "cidade": "Badajoz", "pais": "Espanha"},
        {"codigo": "MAD", "nome": "Adolfo Suárez Madrid–Barajas", "cidade": "Madrid", "pais": "Espanha"},
        {"codigo": "BCN", "nome": "Barcelona-El Prat Airport", "cidade": "Barcelona", "pais": "Espanha"},
        {"codigo": "CDG", "nome": "Charles de Gaulle Airport", "cidade": "Paris", "pais": "França"},
        {"codigo": "ZRH", "nome": "Zurich Airport", "cidade": "Zurique", "pais": "Suíça"},
        {"codigo": "AMS", "nome": "Amsterdam Schiphol Airport", "cidade": "Amsterdam", "pais": "Países Baixos"},
        {"codigo": "LHR", "nome": "Heathrow Airport", "cidade": "Londres", "pais": "Reino Unido"},
        {"codigo": "LGW", "nome": "Gatwick Airport", "cidade": "Londres", "pais": "Reino Unido"},
        {"codigo": "MXP", "nome": "Milano Malpensa Airport", "cidade": "Milão", "pais": "Itália"},
        {"codigo": "LIN", "nome": "Milano Linate Airport", "cidade": "Milão", "pais": "Itália"}
    ]

    # Coordenadas aproximadas dos aeroportos (lat, lon)
    coordenadas = {
        "LIS": (38.7813, -9.1361),
        "OPO": (41.2481, -8.6814),
        "FAO": (37.0144, -7.9658),
        "BJZ": (38.8906, -6.8213),
        "MAD": (40.4719, -3.5626),
        "BCN": (41.2974, 2.0833),
        "CDG": (49.0097, 2.5479),
        "ZRH": (47.4647, 8.5492),
        "AMS": (52.3105, 4.7683),
        "LHR": (51.4700, -0.4543),
        "LGW": (51.1481, -0.1903),
        "MXP": (45.6306, 8.7281),
        "LIN": (45.4454, 9.2761)
    }

    # Funções auxiliares comuns
    def calcular_distancia(coord1, coord2):
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Raio da Terra em km
        
        return c * r

    def is_same_city_flight(origem, destino):
        """Retorna True se o voo é entre aeroportos da mesma cidade proibidos."""
        same_city_pairs = {("LGW", "LHR"), ("LHR", "LGW"), ("MXP", "LIN"), ("LIN", "MXP")}
        return (origem, destino) in same_city_pairs

    # Criar tabela de durações fixas para cada par de aeroportos (em minutos)
    duracoes_voo = {}
    velocidade_padrao = 850  # km/h

    for aeroporto1 in aeroportos:
        for aeroporto2 in aeroportos:
            if aeroporto1["codigo"] != aeroporto2["codigo"]:
                coord1 = coordenadas[aeroporto1["codigo"]]
                coord2 = coordenadas[aeroporto2["codigo"]]
                distancia = calcular_distancia(coord1, coord2)
                duracao = max(45, int(distancia / velocidade_padrao * 60))  # Mínimo 45 min
                duracoes_voo[(aeroporto1["codigo"], aeroporto2["codigo"])] = duracao

    # PARTE 1: GERAR VOOS PARA 2024 (exatamente 5 por dia)
    # Inicializar estado dos aviões para 2024
    estado_avioes = {}
    airports = [a["codigo"] for a in aeroportos]
    
    for aviao in avioes:
        estado_avioes[aviao["no_serie"]] = {
            "aeroporto_atual": random.choice(airports),
            "ultima_chegada": datetime.datetime(2023, 12, 31, 23, 59, 59)
        }

    voos_2024 = []
    voos_existentes = set()  # Para garantir unicidade
    
    # Período de geração de voos para 2024
    data_inicio_2024 = datetime.date(2024, 1, 1)
    data_fim_2024 = datetime.date(2024, 12, 31)
    
    # Gerar voos dia por dia para 2024
    data_atual = data_inicio_2024
    while data_atual <= data_fim_2024:
        voos_dia = gerar_exatos_5_voos_dia(
            data_atual, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes
        )
        
        # Adicionar voos do dia
        for voo in voos_dia:
            voos_2024.append(voo)
        
        data_atual += datetime.timedelta(days=1)

    # PARTE 2: GERAR VOOS PARA 2025 (janeiro a julho)
    # Estado dos aviões já está correto após gerar 2024
    # Continuamos usando o mesmo estado_avioes e voos_existentes
    
    voos_2025 = []
    
    # Período de geração de voos para 2025
    data_inicio_2025 = datetime.date(2025, 1, 1)
    data_fim_2025 = datetime.date(2025, 7, 31)
    
    # Gerar voos dia por dia para 2025
    data_atual = data_inicio_2025
    while data_atual <= data_fim_2025:
        voos_dia = gerar_voos_dia(
            data_atual, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes
        )
        
        # Adicionar voos do dia
        for voo in voos_dia:
            voos_2025.append(voo)
        
        data_atual += datetime.timedelta(days=1)
    
    # Salvar resultados em arquivos separados
    salvar_voos_sql(voos_2024, "voos_2024.sql", "2024", "1 de Janeiro a 31 de Dezembro de 2024")
    salvar_voos_sql(voos_2025, "voos_2025.sql", "2025", "1 de Janeiro a 31 de Julho de 2025")

    # Arquivo combinado opcional
    # salvar_voos_sql(voos_2024 + voos_2025, "voos_2024_2025.sql", "2024-2025", "1 de Janeiro de 2024 a 31 de Julho de 2025")
    
    return len(voos_2024), len(voos_2025)

def gerar_exatos_5_voos_dia(data, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes):
    """
    Gera exatamente 5 voos por dia, com todas as restrições:
    - Sem voos duplicados (mesmo horário, origem, destino)
    - Aviões não teleportam (partem de onde estão)
    - Voos proibidos entre aeroportos da mesma cidade
    - Horários realistas (5h-21h partida, chegada até 23h)
    """
    voos_dia = []
    airports = [a["codigo"] for a in aeroportos]
    plane_list = [a["no_serie"] for a in avioes]
    
    # Definir 5 slots de tempo fixos ao longo do dia
    slots_base = [
        datetime.time(6, 0),   # Manhã cedo
        datetime.time(9, 30),  # Manhã
        datetime.time(13, 0),  # Tarde
        datetime.time(16, 30), # Tarde final
        datetime.time(20, 0)   # Noite
    ]
    
    tentativas_maximas = 100  # Evitar loop infinito
    
    for tentativa in range(tentativas_maximas):
        if len(voos_dia) >= 5:
            break
            
        # Escolher slot aleatório
        slot = random.choice(slots_base)
        
        # Escolher avião aleatório
        plane = random.choice(plane_list)
        origem = estado_avioes[plane]["aeroporto_atual"]
        ultima_chegada = estado_avioes[plane]["ultima_chegada"]
        
        # Calcular horário de partida
        t_dep = datetime.datetime.combine(data, slot)
        
        # Garantir que passa pelo menos 1h desde a última chegada
        if ultima_chegada + datetime.timedelta(hours=1) > t_dep:
            t_dep = ultima_chegada + datetime.timedelta(hours=1)
        
        # Não permitir partidas depois das 21h
        if t_dep.time() > datetime.time(21, 0):
            continue
            
        # Escolher destino válido
        destinos_possiveis = [a for a in airports if a != origem and not is_same_city_flight(origem, a)]
        
        if not destinos_possiveis:
            continue
            
        destino = random.choice(destinos_possiveis)
        
        # Calcular duração e chegada
        duracao = duracoes_voo.get((origem, destino), 60)
        t_arr = t_dep + datetime.timedelta(minutes=duracao)
        
        # Não permitir chegada depois das 23h
        if t_arr.time() > datetime.time(23, 0):
            continue
        
        # Verificar unicidade - chave: (hora_partida, origem, destino)
        route_time_key = (t_dep.strftime("%Y-%m-%d %H:%M:%S"), origem, destino)
        
        if route_time_key in voos_existentes:
            # Tentar ajustar horário ligeiramente
            voo_ajustado = False
            for ajuste in range(5, 121, 5):  # Ajustar de 5 em 5 minutos até 2h
                t_dep_ajustado = t_dep + datetime.timedelta(minutes=ajuste)
                
                if t_dep_ajustado.time() > datetime.time(21, 0):
                    break
                    
                t_arr_ajustado = t_dep_ajustado + datetime.timedelta(minutes=duracao)
                
                if t_arr_ajustado.time() > datetime.time(23, 0):
                    break
                    
                route_time_key_ajustado = (t_dep_ajustado.strftime("%Y-%m-%d %H:%M:%S"), origem, destino)
                
                if route_time_key_ajustado not in voos_existentes:
                    t_dep = t_dep_ajustado
                    t_arr = t_arr_ajustado
                    route_time_key = route_time_key_ajustado
                    voo_ajustado = True
                    break
            
            if not voo_ajustado:
                continue  # Não conseguiu encontrar horário disponível
        
        # Verificar se o avião está disponível no horário ajustado
        if ultima_chegada + datetime.timedelta(hours=1) > t_dep:
            continue
        
        # Criar o voo
        voo = {
            "no_serie": plane,
            "hora_partida": t_dep.strftime("%Y-%m-%d %H:%M:%S"),
            "hora_chegada": t_arr.strftime("%Y-%m-%d %H:%M:%S"),
            "partida": origem,
            "chegada": destino
        }
        
        voos_dia.append(voo)
        voos_existentes.add(route_time_key)
        
        # Atualizar estado do avião
        estado_avioes[plane]["aeroporto_atual"] = destino
        estado_avioes[plane]["ultima_chegada"] = t_arr
    
    return voos_dia

def gerar_voos_dia(data, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes):
    """
    Gera voos para um dia de forma otimizada (para 2025):
    - Cada avião voa em cada slot, se possível.
    - Aviões são distribuídos de forma a evitar longos períodos parados.
    - Horários são espaçados para cobrir o dia todo.
    """
    voos_dia = []
    airports = [a["codigo"] for a in aeroportos]
    plane_list = [a["no_serie"] for a in avioes]
    slot_interval = 2  # horas entre slots
    slots = [datetime.time(hour, 0) for hour in range(5, 22, slot_interval)]

    for slot in slots:
        # Para cada avião, tente agendar um voo a partir do aeroporto atual
        for plane in plane_list:
            origem = estado_avioes[plane]["aeroporto_atual"]
            ultima_chegada = estado_avioes[plane]["ultima_chegada"]
            
            # Calcular horário de partida para este slot
            t_dep = datetime.datetime.combine(data, slot)
            
            # Garantir que passa pelo menos 1h desde a última chegada
            if ultima_chegada + datetime.timedelta(hours=1) > t_dep:
                t_dep = ultima_chegada + datetime.timedelta(hours=1)
            
            # Não permitir partidas depois das 21h
            if t_dep.time() > datetime.time(21, 0):
                continue
                
            # Escolher destino diferente do atual
            destinos_possiveis = [a for a in airports if a != origem]
            random.shuffle(destinos_possiveis)
            
            voo_agendado = False
            for destino in destinos_possiveis:
                # Verificar se é voo proibido (mesma cidade)
                if is_same_city_flight(origem, destino):
                    continue
                
                # Calcular duração e chegada
                duracao = duracoes_voo.get((origem, destino), 60)
                t_arr = t_dep + datetime.timedelta(minutes=duracao)
                
                # Não permitir chegada depois das 23h
                if t_arr.time() > datetime.time(23, 0):
                    continue
                
                # Verificar unicidade (hora_partida, partida, chegada)
                route_time_key = (t_dep.strftime("%Y-%m-%d %H:%M:%S"), origem, destino)
                if route_time_key in voos_existentes:
                    # Tentar ajustar horário ligeiramente
                    for ajuste in range(5, 61, 5):  # Ajustar de 5 em 5 minutos
                        t_dep_ajustado = t_dep + datetime.timedelta(minutes=ajuste)
                        if t_dep_ajustado.time() > datetime.time(21, 0):
                            break
                        t_arr_ajustado = t_dep_ajustado + datetime.timedelta(minutes=duracao)
                        if t_arr_ajustado.time() > datetime.time(23, 0):
                            break
                        route_time_key_ajustado = (t_dep_ajustado.strftime("%Y-%m-%d %H:%M:%S"), origem, destino)
                        if route_time_key_ajustado not in voos_existentes:
                            t_dep = t_dep_ajustado
                            t_arr = t_arr_ajustado
                            route_time_key = route_time_key_ajustado
                            break
                    else:
                        continue  # Não conseguiu encontrar horário disponível
                
                # Criar o voo
                voo = {
                    "no_serie": plane,
                    "hora_partida": t_dep.strftime("%Y-%m-%d %H:%M:%S"),
                    "hora_chegada": t_arr.strftime("%Y-%m-%d %H:%M:%S"),
                    "partida": origem,
                    "chegada": destino
                }
                
                voos_dia.append(voo)
                voos_existentes.add(route_time_key)
                
                # Atualizar estado do avião
                estado_avioes[plane]["aeroporto_atual"] = destino
                estado_avioes[plane]["ultima_chegada"] = t_arr
                
                voo_agendado = True
                break
            
            # Se não conseguiu agendar voo, o avião fica parado até o próximo slot

    return voos_dia

def is_same_city_flight(origem, destino):
    '''Retorna True se o voo é entre aeroportos da mesma cidade proibidos.'''
    same_city_pairs = {("LGW", "LHR"), ("LHR", "LGW"), ("MXP", "LIN"), ("LIN", "MXP")}
    return (origem, destino) in same_city_pairs


def salvar_voos_sql(voos, nome_arquivo, ano, periodo_desc):
    """Salva a lista de voos em um arquivo SQL"""
    sql_content = f"-- Voos gerados automaticamente para {ano}\n"
    sql_content += f"-- Período: {periodo_desc}\n"
    sql_content += f"-- Total de voos: {len(voos)}\n\n"
    
    # Inserir voos em lotes
    batch_size = 100
    for i in range(0, len(voos), batch_size):
        batch = voos[i:i+batch_size]
        sql_content += "INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES\n"
        
        valores = []
        for voo in batch:
            valores.append(f"('{voo['no_serie']}', '{voo['hora_partida']}', '{voo['hora_chegada']}', '{voo['partida']}', '{voo['chegada']}')")
        
        sql_content += ",\n".join(valores) + ";\n\n"
    
    # Salvar no ficheiro
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print(f"Ficheiro SQL gerado com {len(voos)} voos para {ano}!")
    print(f"Ficheiro salvo como: {nome_arquivo}")

# Executar o gerador
if __name__ == "__main__":
    voos_2024, voos_2025 = gerar_voos_2024_2025()
    print(f"Total de voos gerados: {voos_2024 + voos_2025}")