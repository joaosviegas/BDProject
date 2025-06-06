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
    """Gera voos maximizados para junho com distribuição equilibrada ao longo do dia"""
    voos_dia = []
    
    # Define time slots throughout the day
    time_slots = [
        (datetime.time(5, 0), datetime.time(8, 59)),   # Early morning
        (datetime.time(9, 0), datetime.time(11, 59)),  # Morning
        (datetime.time(12, 0), datetime.time(14, 59)), # Early afternoon
        (datetime.time(15, 0), datetime.time(17, 59)), # Late afternoon
        (datetime.time(18, 0), datetime.time(21, 59))  # Evening
    ]
    
    # Track flights per origin-destination pair per time slot
    flight_distribution = {}
    for origem in [a["codigo"] for a in aeroportos]:
        flight_distribution[origem] = {}
        for destino in [a["codigo"] for a in aeroportos]:
            if origem != destino:
                flight_distribution[origem][destino] = [0 for _ in range(len(time_slots))]
    
    # PHASE 1: First ensure broad coverage across all airports and time slots
    # Go through each origin airport
    for origem in [a["codigo"] for a in aeroportos]:
        # For each time slot
        for slot_idx, (time_start, time_end) in enumerate(time_slots):
            # Get all possible destinations, prioritize those with fewer flights in this time slot
            destinos = sorted(
                [d["codigo"] for d in aeroportos if d["codigo"] != origem],
                key=lambda dest: flight_distribution[origem].get(dest, [0]*len(time_slots))[slot_idx]
            )
            
            # Try to schedule a flight to each destination in this time slot
            for destino in destinos:
                # Find an available plane at this origin
                aviao_disponivel = None
                for aviao in avioes:
                    no_serie = aviao["no_serie"]
                    ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
                    
                    # Check if plane is either at the origin, or can be repositioned
                    if estado_avioes[no_serie]["aeroporto_atual"] != origem:
                        continue
                    
                    # Calculate earliest departure time
                    earliest_departure = max(
                        ultima_chegada + datetime.timedelta(hours=1),
                        datetime.datetime.combine(data, time_start)
                    )
                    
                    # Check if within the time slot
                    if earliest_departure.time() <= time_end:
                        aviao_disponivel = (no_serie, earliest_departure)
                        break
                
                # If found a plane, schedule the flight
                if aviao_disponivel:
                    no_serie, departure_time = aviao_disponivel
                    duracao = duracoes_voo.get((origem, destino))
                    if not duracao:
                        continue
                    
                    # Create flight
                    voo = criar_voo_direto_unico(no_serie, origem, destino, 
                                               departure_time, duracao, 
                                               estado_avioes, voos_existentes)
                    
                    if voo:
                        voos_dia.append(voo)
                        # Update tracking structures
                        actual_departure = datetime.datetime.strptime(voo['hora_partida'], "%Y-%m-%d %H:%M:%S")
                        for i, (start, end) in enumerate(time_slots):
                            if start <= actual_departure.time() <= end:
                                flight_distribution[origem][destino][i] += 1
                                break
    
    # PHASE 2: Fill gaps in the schedule - address underserved airports and time slots
    # Identify the most underserved origin-destination-timeslot combinations
    underserved_combinations = []
    for origem in flight_distribution:
        for destino in flight_distribution[origem]:
            for slot_idx, count in enumerate(flight_distribution[origem][destino]):
                if count < 1:  # Underserved if less than 1 flight
                    underserved_combinations.append((origem, destino, slot_idx, count))
    
    # Sort by count (least served first)
    underserved_combinations.sort(key=lambda x: x[3])
    
    # Try to address underserved routes
    for origem, destino, slot_idx, _ in underserved_combinations:
        time_start, time_end = time_slots[slot_idx]
        
        # Try to reposition planes if needed
        for aviao in avioes:
            no_serie = aviao["no_serie"]
            ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
            aeroporto_atual = estado_avioes[no_serie]["aeroporto_atual"]
            
            # Calculate earliest departure time
            earliest_possible = max(
                ultima_chegada + datetime.timedelta(hours=1),
                datetime.datetime.combine(data, time_start)
            )
            
            # Skip if not possible within time slot
            if earliest_possible.time() > time_end:
                continue
            
            # If plane not at origin, try to reposition it first
            if aeroporto_atual != origem:
                duracao_posicionamento = duracoes_voo.get((aeroporto_atual, origem))
                if not duracao_posicionamento:
                    continue
                
                # Create positioning flight
                voo_posicionamento = criar_voo_direto_unico(
                    no_serie, aeroporto_atual, origem,
                    earliest_possible, duracao_posicionamento,
                    estado_avioes, voos_existentes
                )
                
                if voo_posicionamento:
                    voos_dia.append(voo_posicionamento)
                    # Update earliest departure time after positioning
                    earliest_possible = datetime.datetime.strptime(
                        voo_posicionamento['hora_chegada'], "%Y-%m-%d %H:%M:%S"
                    ) + datetime.timedelta(minutes=30)
                else:
                    continue
            
            # Now create the actual flight to the destination
            if earliest_possible.time() <= time_end:
                duracao = duracoes_voo.get((origem, destino))
                if not duracao:
                    continue
                
                voo = criar_voo_direto_unico(
                    no_serie, origem, destino,
                    earliest_possible, duracao,
                    estado_avioes, voos_existentes
                )
                
                if voo:
                    voos_dia.append(voo)
                    # Update tracking
                    actual_departure = datetime.datetime.strptime(voo['hora_partida'], "%Y-%m-%d %H:%M:%S")
                    for i, (start, end) in enumerate(time_slots):
                        if start <= actual_departure.time() <= end:
                            flight_distribution[origem][destino][i] += 1
                            break
                    break  # Move to next underserved combination
    
    # PHASE 3: Maximize flight count - continue adding flights where possible
    tentativas_sem_sucesso = 0
    max_tentativas = 30
    
    while tentativas_sem_sucesso < max_tentativas:
        voo_criado = False
        
        # Find origins with the fewest departures
        departures_per_airport = {}
        for origem in [a["codigo"] for a in aeroportos]:
            departures_per_airport[origem] = sum(
                flight_distribution[origem][dest][slot_idx] 
                for dest in flight_distribution[origem] 
                for slot_idx in range(len(time_slots))
            )
        
        # Sort airports by number of departures (least first)
        aeroportos_sorted = sorted(
            [a["codigo"] for a in aeroportos],
            key=lambda code: departures_per_airport[code]
        )
        
        # Try each origin, prioritizing least served
        for origem in aeroportos_sorted:
            # For each time slot
            for slot_idx, (time_start, time_end) in enumerate(time_slots):
                # Find destinations with fewest flights from this origin in this time slot
                destinos = sorted(
                    [d["codigo"] for d in aeroportos if d["codigo"] != origem],
                    key=lambda dest: flight_distribution[origem].get(dest, [0]*len(time_slots))[slot_idx]
                )
                
                # Try each destination
                for destino in destinos[:5]:  # Limit to top 5 to avoid too much LIS-OPO
                    # Find planes at this origin available in this time slot
                    avioes_disponiveis = []
                    for aviao in avioes:
                        no_serie = aviao["no_serie"]
                        if estado_avioes[no_serie]["aeroporto_atual"] == origem:
                            ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
                            earliest_departure = max(
                                ultima_chegada + datetime.timedelta(hours=1),
                                datetime.datetime.combine(data, time_start)
                            )
                            
                            if earliest_departure.time() <= time_end:
                                avioes_disponiveis.append((no_serie, earliest_departure))
                    
                    if not avioes_disponiveis:
                        continue
                    
                    # Sort by earliest availability
                    avioes_disponiveis.sort(key=lambda x: x[1])
                    
                    # Try each plane
                    for no_serie, departure_time in avioes_disponiveis:
                        duracao = duracoes_voo.get((origem, destino))
                        if not duracao:
                            continue
                        
                        arrival_time = departure_time + datetime.timedelta(minutes=duracao)
                        if arrival_time.time() <= datetime.time(23, 0):
                            voo = criar_voo_direto_unico(
                                no_serie, origem, destino,
                                departure_time, duracao,
                                estado_avioes, voos_existentes
                            )
                            
                            if voo:
                                voos_dia.append(voo)
                                voo_criado = True
                                # Update tracking
                                actual_departure = datetime.datetime.strptime(voo['hora_partida'], "%Y-%m-%d %H:%M:%S")
                                for i, (start, end) in enumerate(time_slots):
                                    if start <= actual_departure.time() <= end:
                                        flight_distribution[origem][destino][i] += 1
                                        break
                                break
                    
                    if voo_criado:
                        break
                
                if voo_criado:
                    break
            
            if voo_criado:
                break
        
        if not voo_criado:
            tentativas_sem_sucesso += 1
        else:
            tentativas_sem_sucesso = 0
    
    # PHASE 4: Ensure return flights for all routes
    
    # Track all routes that had flights today
    routes_flown = {}
    for voo in voos_dia:
        origem = voo['partida']
        destino = voo['chegada']
        key = (origem, destino)
        if key not in routes_flown:
            routes_flown[key] = 0
        routes_flown[key] += 1
    
    # Ensure each route has roughly the same number of flights in both directions
    for (origem, destino), count in routes_flown.items():
        reverse_route = (destino, origem)
        reverse_count = routes_flown.get(reverse_route, 0)
        
        # If there's an imbalance, try to add return flights
        flights_to_add = max(0, count - reverse_count)
        
        for _ in range(flights_to_add):
            # Find an available plane at the destination airport
            avioes_no_destino = []
            for aviao in avioes:
                no_serie = aviao["no_serie"]
                if estado_avioes[no_serie]["aeroporto_atual"] == destino:
                    ultima_chegada = estado_avioes[no_serie]["ultima_chegada"]
                    proximo_horario_possivel = max(
                        ultima_chegada + datetime.timedelta(hours=1),
                        datetime.datetime.combine(data, datetime.time(5, 0))
                    )
                    if proximo_horario_possivel.time() <= datetime.time(21, 0):
                        avioes_no_destino.append((no_serie, proximo_horario_possivel))
            
            if not avioes_no_destino:
                continue
            
            # Sort by earliest availability
            avioes_no_destino.sort(key=lambda x: x[1])
            
            # Try to create the return flight
            for no_serie, departure_time in avioes_no_destino:
                duracao = duracoes_voo.get((destino, origem))
                if not duracao:
                    continue
                
                arrival_time = departure_time + datetime.timedelta(minutes=duracao)
                if arrival_time.time() <= datetime.time(23, 0):
                    voo = criar_voo_direto_unico(
                        no_serie, destino, origem,
                        departure_time, duracao,
                        estado_avioes, voos_existentes
                    )
                    
                    if voo:
                        voos_dia.append(voo)
                        # Update route counters
                        if reverse_route not in routes_flown:
                            routes_flown[reverse_route] = 0
                        routes_flown[reverse_route] += 1
                        break
    
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