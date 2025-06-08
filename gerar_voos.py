import datetime
import random
import math
from itertools import combinations

def gerar_voos_sql():
    # Definição dos aviões
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

    # Definição dos aeroportos
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
        {"codigo": "MXP", "nome": "Milano Malpensa Airport", "cidade": "MIlão", "pais": "Itália"},
        {"codigo": "LIN", "nome": "Milano Linate Airport", "cidade": "MIlão", "pais": "Itália"}
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

    # Função para calcular distância entre aeroportos
    def calcular_distancia(coord1, coord2):
        lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
        lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Raio da Terra em km
        
        return c * r

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

    # Estado atual de cada avião (localização e hora da última chegada)
    estado_avioes = {}
    for aviao in avioes:
        # Inicializar aviões em aeroportos aleatórios
        aeroporto_inicial = random.choice(aeroportos)["codigo"]
        estado_avioes[aviao["no_serie"]] = {
            "aeroporto_atual": aeroporto_inicial,
            "ultima_chegada": datetime.datetime(2024, 12, 31, 23, 59, 59)
        }

    voos = []
    voos_existentes = set()  # Para garantir unicidade
    
    # Período de geração de voos
    data_inicio = datetime.date(2025, 1, 1)
    data_fim = datetime.date(2025, 7, 31)
    
    # Todas as rotas possíveis
    todas_rotas = []
    for aeroporto1 in aeroportos:
        for aeroporto2 in aeroportos:
            if aeroporto1["codigo"] != aeroporto2["codigo"]:
                todas_rotas.append((aeroporto1["codigo"], aeroporto2["codigo"]))

    # Gerar voos dia por dia
    data_atual = data_inicio
    while data_atual <= data_fim:
        if data_atual.month == 6:  # Junho - maximizar voos
            voos_dia = gerar_voos_junho(data_atual, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes)
        else:  # Janeiro a Maio e Julho - mínimo 5 voos por dia
            voos_dia = gerar_voos_normais(data_atual, aeroportos, avioes, duracoes_voo, estado_avioes, 5, voos_existentes)
        
        # Adicionar voos do dia
        for voo in voos_dia:
            voos.append(voo)
        
        data_atual += datetime.timedelta(days=1)

    # Gerar SQL
    sql_content = "-- Voos gerados automaticamente\n"
    sql_content += "-- Período: 1 de Janeiro a 31 de Julho de 2025\n\n"
    
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
    with open("voos_database.sql", "w", encoding="utf-8") as f:
        f.write(sql_content)
    
    print(f"Ficheiro SQL gerado com {len(voos)} voos!")
    print("Ficheiro salvo como: voos_database.sql")
    
    return sql_content

def is_same_city_flight(origem, destino):
    '''Retorna True se o voo é entre aeroportos da mesma cidade proibidos.'''
    same_city_pairs = {("LGW", "LHR"), ("LHR", "LGW"), ("MXP", "LIN"), ("LIN", "MXP")}
    return (origem, destino) in same_city_pairs

def gerar_voos_normais(data, aeroportos, avioes, duracoes_voo, estado_avioes, min_voos, voos_existentes):
    """Gera voos normais garantindo mínimo de voos por dia e voos de retorno"""
    voos_dia = []
    voos_retorno_pendentes = []
    
    # Garantir pelo menos min_voos voos
    for _ in range(min_voos):
        aviao_disponivel = encontrar_aviao_disponivel(avioes, estado_avioes, data)
        if not aviao_disponivel:
            break
            
        origem = estado_avioes[aviao_disponivel]["aeroporto_atual"]
        destino = random.choice([a["codigo"] for a in aeroportos if a["codigo"] != origem])
        
        voo_ida = criar_voo_unico(aviao_disponivel, origem, destino, data, duracoes_voo, estado_avioes, voos_existentes)
        if voo_ida:
            voos_dia.append(voo_ida)
            # Agendar voo de retorno
            voos_retorno_pendentes.append((aviao_disponivel, destino, origem))
    
    # Processar voos de retorno
    for aviao, origem, destino in voos_retorno_pendentes:
        voo_retorno = criar_voo_unico(aviao, origem, destino, data, duracoes_voo, estado_avioes, voos_existentes)
        
        if voo_retorno:
            voos_dia.append(voo_retorno)
    
    return voos_dia

def gerar_voos_junho(data, aeroportos, avioes, duracoes_voo, estado_avioes, voos_existentes):
    """
    Gera voos para junho de forma otimizada:
    - Cada avião voa em cada slot, se possível.
    - Cada voo tem retorno.
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
            t_dep = max(datetime.datetime.combine(data, slot), ultima_chegada + datetime.timedelta(hours=1))
            if t_dep.time() > datetime.time(21, 0):
                continue
            # Escolher destino diferente do atual
            destinos_possiveis = [a for a in airports if a != origem]
            random.shuffle(destinos_possiveis)
            voo_agendado = False
            for destino in destinos_possiveis:
                if is_same_city_flight(origem, destino):
                    # Se for voo entre aeroportos da mesma cidade, não agendar
                    continue
                duracao = duracoes_voo.get((origem, destino), 60)
                t_arr = t_dep + datetime.timedelta(minutes=duracao)
                route_time_key = (t_dep.strftime("%Y-%m-%d %H:%M:%S"), origem, destino)
                if route_time_key in voos_existentes:
                    continue
                # Não permitir chegada depois das 23h
                if t_arr.time() > datetime.time(23, 0):
                    continue
                voo = {
                    "no_serie": plane,
                    "hora_partida": t_dep.strftime("%Y-%m-%d %H:%M:%S"),
                    "hora_chegada": t_arr.strftime("%Y-%m-%d %H:%M:%S"),
                    "partida": origem,
                    "chegada": destino
                }
                voos_dia.append(voo)
                voos_existentes.add(route_time_key)
                estado_avioes[plane]["aeroporto_atual"] = destino
                estado_avioes[plane]["ultima_chegada"] = t_arr
                voo_agendado = True
                break
            # Se não conseguiu agendar voo, o avião fica parado até o próximo slot

    return voos_dia

def encontrar_aviao_disponivel(avioes, estado_avioes, data):
    """Encontra um avião disponível para voar"""
    avioes_disponiveis = []
    
    for aviao in avioes:
        no_serie = aviao["no_serie"]
        ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
        
        # Verificar se o avião está disponível (2 horas de intervalo mínimo)
        inicio_dia = datetime.datetime.combine(data, datetime.time(5, 0))
        if ultima_chegada + datetime.timedelta(hours=2) <= inicio_dia:
            avioes_disponiveis.append(no_serie)
    
    return random.choice(avioes_disponiveis) if avioes_disponiveis else None

def encontrar_aviao_mais_proximo(avioes, estado_avioes, aeroporto_origem, data):
    """Encontra o avião mais próximo ou já no aeroporto de origem"""
    avioes_no_aeroporto = []
    avioes_disponiveis = []
    
    for aviao in avioes:
        no_serie = aviao["no_serie"]
        aeroporto_atual = estado_avioes[no_serie]["aeroporto_atual"]
        ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
        
        # Verificar disponibilidade
        inicio_dia = datetime.datetime.combine(data, datetime.time(5, 0))
        if ultima_chegada + datetime.timedelta(hours=2) <= inicio_dia:
            if aeroporto_atual == aeroporto_origem:
                avioes_no_aeroporto.append(no_serie)
            else:
                avioes_disponiveis.append(no_serie)
    
    # Preferir aviões já no aeroporto
    if avioes_no_aeroporto:
        return random.choice(avioes_no_aeroporto)
    elif avioes_disponiveis:
        return random.choice(avioes_disponiveis)
    
    return None

def criar_voo_unico(no_serie, origem, destino, data, duracoes_voo, estado_avioes, voos_existentes):
    """Cria um voo único (não duplicado)"""
    voo = criar_voo(no_serie, origem, destino, data, duracoes_voo, estado_avioes)
    if voo:
        # Check uniqueness based on departure time, origin, and destination (database constraint)
        route_time_key = (voo['hora_partida'], voo['partida'], voo['chegada'])
        
        # If this combination already exists, adjust the departure time slightly
        original_dt = datetime.datetime.strptime(voo['hora_partida'], "%Y-%m-%d %H:%M:%S")
        attempt = 0
        
        while route_time_key in voos_existentes and attempt < 12:
            # Add 5 minutes to departure time
            attempt += 1
            adjusted_dt = original_dt + datetime.timedelta(minutes=5*attempt)
            
            # Skip if this pushes beyond acceptable hours
            if adjusted_dt.time() > datetime.time(21, 0):
                return None
                
            # Recalculate arrival time based on new departure
            duracao = duracoes_voo.get((origem, destino), 60)
            adjusted_arrival = adjusted_dt + datetime.timedelta(minutes=duracao)
            
            # Update the voo dictionary
            voo['hora_partida'] = adjusted_dt.strftime("%Y-%m-%d %H:%M:%S")
            voo['hora_chegada'] = adjusted_arrival.strftime("%Y-%m-%d %H:%M:%S")
            
            # Update the uniqueness check key
            route_time_key = (voo['hora_partida'], voo['partida'], voo['chegada'])
        
        # If we found a unique time slot, or if it was unique to begin with
        if route_time_key not in voos_existentes:
            # Track both the aircraft-specific key and the database constraint key
            voos_existentes.add(route_time_key)
            plane_key = (voo['no_serie'], voo['hora_partida'], voo['partida'], voo['chegada'])
            voos_existentes.add(plane_key)
            
            # Update the aircraft's state with the possibly adjusted time
            estado_avioes[no_serie]["ultima_chegada"] = datetime.datetime.strptime(
                voo['hora_chegada'], "%Y-%m-%d %H:%M:%S")
            
            return voo
    return None

def criar_voo_direto_unico(no_serie, origem, destino, horario_partida, duracao, estado_avioes, voos_existentes):
    """Cria um voo direto único com horário específico"""
    voo = criar_voo_direto(no_serie, origem, destino, horario_partida, duracao, estado_avioes)
    if voo:
        # Check uniqueness based on departure time, origin, and destination (database constraint)
        route_time_key = (voo['hora_partida'], voo['partida'], voo['chegada'])
        
        # If this combination already exists, adjust the departure time slightly
        original_dt = datetime.datetime.strptime(voo['hora_partida'], "%Y-%m-%d %H:%M:%S")
        attempt = 0
        
        while route_time_key in voos_existentes and attempt < 12:
            # Add 5 minutes to departure time
            attempt += 1
            adjusted_dt = original_dt + datetime.timedelta(minutes=5*attempt)
            
            # Skip if this pushes beyond acceptable hours
            if adjusted_dt.time() > datetime.time(21, 0):
                return None
                
            # Recalculate arrival time based on new departure
            adjusted_arrival = adjusted_dt + datetime.timedelta(minutes=duracao)
            
            # Update the voo dictionary
            voo['hora_partida'] = adjusted_dt.strftime("%Y-%m-%d %H:%M:%S")
            voo['hora_chegada'] = adjusted_arrival.strftime("%Y-%m-%d %H:%M:%S")
            
            # Update the uniqueness check key
            route_time_key = (voo['hora_partida'], voo['partida'], voo['chegada'])
        
        # If we found a unique time slot, or if it was unique to begin with
        if route_time_key not in voos_existentes:
            # Track both keys for completeness
            voos_existentes.add(route_time_key)
            plane_key = (voo['no_serie'], voo['hora_partida'], voo['partida'], voo['chegada'])
            voos_existentes.add(plane_key)
            
            # Update the aircraft's state with the possibly adjusted time
            estado_avioes[no_serie]["ultima_chegada"] = datetime.datetime.strptime(
                voo['hora_chegada'], "%Y-%m-%d %H:%M:%S")
            
            return voo
    return None

def criar_voo_direto(no_serie, origem, destino, horario_partida, duracao, estado_avioes):
    """Cria um voo direto com horário específico"""
    horario_chegada = horario_partida + datetime.timedelta(minutes=duracao)
    
    # Atualizar estado do avião
    estado_avioes[no_serie]["aeroporto_atual"] = destino
    estado_avioes[no_serie]["ultima_chegada"] = horario_chegada
    
    return {
        "no_serie": no_serie,
        "hora_partida": horario_partida.strftime("%Y-%m-%d %H:%M:%S"),
        "hora_chegada": horario_chegada.strftime("%Y-%m-%d %H:%M:%S"),
        "partida": origem,
        "chegada": destino
    }

def criar_voo(no_serie, origem, destino, data, duracoes_voo, estado_avioes):
    """Cria um voo individual"""
    if is_same_city_flight(origem, destino):
        return None
    duracao = duracoes_voo.get((origem, destino))
    if not duracao:
        return None
    
    # Calcular horário de partida (considerando a última chegada + 2h mínimo)
    ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
    aeroporto_atual = estado_avioes[no_serie]["aeroporto_atual"]
    
    # Se o avião não está no aeroporto de origem, precisa de um voo de posicionamento
    if aeroporto_atual != origem:
        duracao_posicionamento = duracoes_voo.get((aeroporto_atual, origem), 60)
        tempo_posicionamento = datetime.timedelta(minutes=duracao_posicionamento)
        ultima_chegada += tempo_posicionamento + datetime.timedelta(hours=1)
        estado_avioes[no_serie]["aeroporto_atual"] = origem
    
    # Calcular horário de partida
    horario_partida = max(
        ultima_chegada + datetime.timedelta(hours=2),
        datetime.datetime.combine(data, datetime.time(5, 0))
    )
    
    # Garantir que não ultrapassa 23:00
    if horario_partida.time() > datetime.time(21, 0):
        return None
    
    horario_chegada = horario_partida + datetime.timedelta(minutes=duracao)
    
    # Atualizar estado do avião
    estado_avioes[no_serie]["aeroporto_atual"] = destino
    estado_avioes[no_serie]["ultima_chegada"] = horario_chegada
    
    return {
        "no_serie": no_serie,
        "hora_partida": horario_partida.strftime("%Y-%m-%d %H:%M:%S"),
        "hora_chegada": horario_chegada.strftime("%Y-%m-%d %H:%M:%S"),
        "partida": origem,
        "chegada": destino
    }

# Executar o gerador
if __name__ == "__main__":
    gerar_voos_sql()