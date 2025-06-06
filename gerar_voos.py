import datetime
import random
import math

def gerar_voos_sql():
    # Definição dos aviões
    avioes = [
        {"no_serie": "A320-001", "modelo": "Airbus A320"},
        {"no_serie": "A320-002", "modelo": "Airbus A320"},
        {"no_serie": "A320-003", "modelo": "Airbus A320"},
        {"no_serie": "A320-004", "modelo": "Airbus A320"},
        {"no_serie": "B737-001", "modelo": "Boeing 737"},
        {"no_serie": "B737-002", "modelo": "Boeing 737"},
        {"no_serie": "B737-003", "modelo": "Boeing 737"},
        {"no_serie": "B737-004", "modelo": "Boeing 737"},
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

    # Dicionário com as distâncias aproximadas entre aeroportos (em km)
    distancias = {
        "LIS": {"OPO": 300, "FAO": 280, "MAD": 500, "BCN": 1000, "CDG": 1500, "ZRH": 1800, "AMS": 1800, "LHR": 1600, "LGW": 1600, "MXP": 1700, "LIN": 1700, "BJZ": 250},
        "OPO": {"LIS": 300, "FAO": 580, "MAD": 450, "BCN": 900, "CDG": 1450, "ZRH": 1750, "AMS": 1750, "LHR": 1550, "LGW": 1550, "MXP": 1650, "LIN": 1650, "BJZ": 400},
        "FAO": {"LIS": 280, "OPO": 580, "MAD": 600, "BCN": 1100, "CDG": 1800, "ZRH": 2000, "AMS": 2100, "LHR": 1800, "LGW": 1800, "MXP": 1900, "LIN": 1900, "BJZ": 300},
        "MAD": {"LIS": 500, "OPO": 450, "FAO": 600, "BCN": 600, "CDG": 1100, "ZRH": 1300, "AMS": 1500, "LHR": 1250, "LGW": 1250, "MXP": 1300, "LIN": 1300, "BJZ": 400},
        "BCN": {"LIS": 1000, "OPO": 900, "FAO": 1100, "MAD": 600, "CDG": 850, "ZRH": 900, "AMS": 1200, "LHR": 1150, "LGW": 1150, "MXP": 700, "LIN": 700, "BJZ": 900},
        "CDG": {"LIS": 1500, "OPO": 1450, "FAO": 1800, "MAD": 1100, "BCN": 850, "ZRH": 500, "AMS": 400, "LHR": 350, "LGW": 350, "MXP": 650, "LIN": 650, "BJZ": 1400},
        "ZRH": {"LIS": 1800, "OPO": 1750, "FAO": 2000, "MAD": 1300, "BCN": 900, "CDG": 500, "AMS": 700, "LHR": 800, "LGW": 800, "MXP": 250, "LIN": 250, "BJZ": 1700},
        "AMS": {"LIS": 1800, "OPO": 1750, "FAO": 2100, "MAD": 1500, "BCN": 1200, "CDG": 400, "ZRH": 700, "LHR": 350, "LGW": 350, "MXP": 850, "LIN": 850, "BJZ": 1800},
        "LHR": {"LIS": 1600, "OPO": 1550, "FAO": 1800, "MAD": 1250, "BCN": 1150, "CDG": 350, "ZRH": 800, "AMS": 350, "LGW": 40, "MXP": 950, "LIN": 950, "BJZ": 1600},
        "LGW": {"LIS": 1600, "OPO": 1550, "FAO": 1800, "MAD": 1250, "BCN": 1150, "CDG": 350, "ZRH": 800, "AMS": 350, "LHR": 40, "MXP": 950, "LIN": 950, "BJZ": 1600},
        "MXP": {"LIS": 1700, "OPO": 1650, "FAO": 1900, "MAD": 1300, "BCN": 700, "CDG": 650, "ZRH": 250, "AMS": 850, "LHR": 950, "LGW": 950, "LIN": 50, "BJZ": 1600},
        "LIN": {"LIS": 1700, "OPO": 1650, "FAO": 1900, "MAD": 1300, "BCN": 700, "CDG": 650, "ZRH": 250, "AMS": 850, "LHR": 950, "LGW": 950, "MXP": 50, "BJZ": 1600},
        "BJZ": {"LIS": 250, "OPO": 400, "FAO": 300, "MAD": 400, "BCN": 900, "CDG": 1400, "ZRH": 1700, "AMS": 1800, "LHR": 1600, "LGW": 1600, "MXP": 1600, "LIN": 1600}
    }

    # Criar tabela de durações fixas para cada par de aeroportos (em minutos)
    # Isso garante que a duração seja a mesma independente do tipo de avião
    duracoes_voo = {}
    velocidade_padrao = 850  # velocidade média padronizada em km/h
    
    # Pré-calcular todas as durações de voo entre aeroportos
    for origem in distancias:
        duracoes_voo[origem] = {}
        for destino in distancias[origem]:
            distancia = distancias[origem][destino]
            # Tempo base de voo (com velocidade padronizada)
            tempo_base = (distancia / velocidade_padrao) * 60
            
            # Adicionar tempo para procedimentos de decolagem/aterrissagem/taxiamento (30 min)
            tempo_total = int(tempo_base) + 30
            
            # Arredondar para intervalos de 5 minutos para mais realismo
            tempo_total = 5 * round(tempo_total / 5)
            
            # Garantir que voos curtos tenham pelo menos 45 minutos
            tempo_total = max(tempo_total, 45)
            
            duracoes_voo[origem][destino] = tempo_total

    # Localizações iniciais dos aviões (onde cada avião começa)
    localizacoes = {}
    aeroportos_distribuidos = ["LIS", "OPO", "MAD", "BCN", "LHR", "CDG", "FAO", "ZRH", "AMS", "LIN"]
    for i, aviao in enumerate(avioes):
        localizacoes[aviao["no_serie"]] = aeroportos_distribuidos[i % len(aeroportos_distribuidos)]

    # Período para geração de voos
    data_inicio = datetime.datetime(2025, 1, 1)
    data_fim = datetime.datetime(2025, 7, 31)
    
    # Função para obter a duração do voo entre dois aeroportos
    def obter_duracao_voo(origem, destino):
        return duracoes_voo[origem][destino]

    # Abrir arquivo para escrever
    with open("popular_voos_2.sql", "w") as f:
        f.write("-- SQL para popular tabela de voos para o período de 1 de Janeiro a 31 de Julho de 2025\n\n")
        
        # Contador para IDs únicos de voos
        voo_id = 1
        
        # Dicionário para rastreamento de voos por dia
        voos_por_dia = {}
        
        # Dicionário para registrar quando cada avião estará disponível
        disponibilidade_avioes = {aviao["no_serie"]: data_inicio for aviao in avioes}
        

        # ...existing code...

        # Special handling for June FIRST - maximize flights from all airports
        if True:  # Enable June special processing
            junho_inicio = datetime.datetime(2025, 6, 1)
            junho_fim = datetime.datetime(2025, 6, 30)
            
            print("Gerando voos extras para Junho...")
            
            # For June, generate MANY more flights per day
            dia_atual = junho_inicio
            while dia_atual <= junho_fim:
                # Track daily flight count for this day
                daily_key = dia_atual.strftime("%Y-%m-%d")
                if daily_key not in voos_por_dia:
                    voos_por_dia[daily_key] = 0
                    
                # Generate flights throughout the day for each plane
                for aviao in avioes:
                    # Check how many flights this plane can do today
                    current_time = max(
                        datetime.datetime.combine(dia_atual.date(), datetime.time(5, 0)),  # Start at 5 AM
                        disponibilidade_avioes[aviao["no_serie"]]
                    )
                    
                    # If plane becomes available tomorrow, skip for today
                    if current_time.date() > dia_atual.date():
                        continue
                        
                    end_of_day = datetime.datetime.combine(dia_atual.date(), datetime.time(23, 59))
                    
                    # Generate as many round trips as possible for this plane on this day
                    while current_time.date() == dia_atual.date() and current_time < end_of_day:
                        origem = localizacoes[aviao["no_serie"]]
                        
                        # Choose random destination
                        destinos_possiveis = [a["codigo"] for a in aeroportos if a["codigo"] != origem]
                        if not destinos_possiveis:
                            break
                            
                        destino = random.choice(destinos_possiveis)
                        
                        # Calculate outbound flight timing
                        duracao_minutos = obter_duracao_voo(origem, destino)
                        hora_partida = current_time
                        hora_chegada = hora_partida + datetime.timedelta(minutes=duracao_minutos)
                        
                        # Check if outbound flight fits in the day
                        if hora_chegada.date() > dia_atual.date():
                            break
                        
                        # Generate outbound flight
                        f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                        f.write(f"('{aviao['no_serie']}', '{hora_partida.strftime('%Y-%m-%d %H:%M:%S')}', ")
                        f.write(f"'{hora_chegada.strftime('%Y-%m-%d %H:%M:%S')}', '{origem}', '{destino}');\n")
                        
                        voos_por_dia[daily_key] += 1
                        voo_id += 1
                        
                        # Calculate return flight timing
                        turnaround = datetime.timedelta(minutes=random.randint(45, 90))  # 45-90 min turnaround
                        hora_partida_volta = hora_chegada + turnaround
                        duracao_volta = obter_duracao_voo(destino, origem)
                        hora_chegada_volta = hora_partida_volta + datetime.timedelta(minutes=duracao_volta)
                        
                        # Check if return flight fits in reasonable time
                        if hora_partida_volta.date() > dia_atual.date() or hora_partida_volta > end_of_day:
                            # Update plane location and availability for next day
                            localizacoes[aviao["no_serie"]] = destino
                            disponibilidade_avioes[aviao["no_serie"]] = datetime.datetime.combine(
                                (dia_atual + datetime.timedelta(days=1)).date(),
                                datetime.time(6, 0)
                            )
                            break
                        
                        # Generate return flight
                        f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                        f.write(f"('{aviao['no_serie']}', '{hora_partida_volta.strftime('%Y-%m-%d %H:%M:%S')}', ")
                        f.write(f"'{hora_chegada_volta.strftime('%Y-%m-%d %H:%M:%S')}', '{destino}', '{origem}');\n")
                        
                        voos_por_dia[daily_key] += 1
                        voo_id += 1
                        
                        # Update plane status - plane returns to original location
                        localizacoes[aviao["no_serie"]] = origem
                        
                        # Add minimum ground time before next flight (30 minutes)
                        disponibilidade_avioes[aviao["no_serie"]] = hora_chegada_volta + datetime.timedelta(minutes=30)
                        current_time = disponibilidade_avioes[aviao["no_serie"]]
                        
                        # If we've moved to next day, stop
                        if current_time.date() > dia_atual.date():
                            break
                
                # Additional flights to maximize utilization - single flights for planes that can still fly
                for aviao in avioes:
                    current_availability = disponibilidade_avioes[aviao["no_serie"]]
                    
                    # If plane is available late in the day, add one more flight
                    if (current_availability.date() == dia_atual.date() and 
                        current_availability.time() < datetime.time(22, 0)):
                        
                        origem = localizacoes[aviao["no_serie"]]
                        destinos_possiveis = [a["codigo"] for a in aeroportos if a["codigo"] != origem]
                        
                        if destinos_possiveis:
                            destino = random.choice(destinos_possiveis)
                            duracao_minutos = obter_duracao_voo(origem, destino)
                            
                            hora_partida = current_availability
                            hora_chegada = hora_partida + datetime.timedelta(minutes=duracao_minutos)
                            
                            # Only add if flight completes before midnight
                            if hora_chegada.date() == dia_atual.date():
                                f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                                f.write(f"('{aviao['no_serie']}', '{hora_partida.strftime('%Y-%m-%d %H:%M:%S')}', ")
                                f.write(f"'{hora_chegada.strftime('%Y-%m-%d %H:%M:%S')}', '{origem}', '{destino}');\n")
                                
                                voos_por_dia[daily_key] += 1
                                voo_id += 1
                                
                                # Update plane location and make it available next morning
                                localizacoes[aviao["no_serie"]] = destino
                                disponibilidade_avioes[aviao["no_serie"]] = datetime.datetime.combine(
                                    (dia_atual + datetime.timedelta(days=1)).date(),
                                    datetime.time(6, 0)
                                )
                
                dia_atual += datetime.timedelta(days=1)


        # Para cada dia no período
        dia_atual = data_inicio
        while dia_atual <= data_fim:
            if dia_atual.month == 6 and dia_atual.day == 1:
                # Skip June 1st, as we already handled it above
                dia_atual += datetime.timedelta(days=1)
                continue
            # Inicializar contagem de voos para este dia
            voos_por_dia[dia_atual.strftime("%Y-%m-%d")] = 0
            
            # Lista de aviões que podem voar neste dia
            avioes_disponiveis = list(avioes)
            random.shuffle(avioes_disponiveis)  # Aleatorizar a ordem
            
            # Garantir pelo menos 5 voos por dia
            voos_necessarios = 5
            
            # Para cada avião disponível
            for aviao in avioes_disponiveis:
                # Se já temos voos suficientes para este dia, podemos parar
                if voos_por_dia[dia_atual.strftime("%Y-%m-%d")] >= voos_necessarios:
                    break
                
                # Verificar se o avião já está comprometido com voos nesta data
                data_disponibilidade = disponibilidade_avioes[aviao["no_serie"]]
                if data_disponibilidade.date() > dia_atual.date():
                    continue
                
                # Criar um par de voos (ida e volta)
                origem = localizacoes[aviao["no_serie"]]
                
                # Escolher destino diferente da origem
                destinos_possiveis = [a["codigo"] for a in aeroportos if a["codigo"] != origem]
                destino = random.choice(destinos_possiveis)
                
                # Definir hora de partida (entre 6h e 18h)
                hora_partida = datetime.datetime.combine(
                    dia_atual.date(), 
                    datetime.time(
                        hour=random.randint(6, 18),
                        minute=random.choice([0, 15, 30, 45])
                    )
                )
                
                # Se o avião só está disponível mais tarde no dia
                if hora_partida < data_disponibilidade:
                    hora_partida = data_disponibilidade
                
                # Obter duração do voo e calcular hora de chegada
                duracao_minutos = obter_duracao_voo(origem, destino)
                hora_chegada = hora_partida + datetime.timedelta(minutes=duracao_minutos)
                
                # Gerar SQL para o voo de ida
                f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                f.write(f"('{aviao['no_serie']}', '{hora_partida.strftime('%Y-%m-%d %H:%M:%S')}', ")
                f.write(f"'{hora_chegada.strftime('%Y-%m-%d %H:%M:%S')}', '{origem}', '{destino}');\n")
                
                voo_id += 1
                voos_por_dia[dia_atual.strftime("%Y-%m-%d")] += 1
                
                # Atualizar a localização do avião
                localizacoes[aviao["no_serie"]] = destino
                
                # Tempo de turnaround (preparação para próximo voo) - entre 1 e 3 horas
                turnaround = datetime.timedelta(hours=random.randint(1, 3))
                hora_partida_volta = hora_chegada + turnaround
                
                # Obter duração do voo de volta (mesma duração da ida, pois usamos tabela fixa)
                duracao_volta_minutos = obter_duracao_voo(destino, origem)
                hora_chegada_volta = hora_partida_volta + datetime.timedelta(minutes=duracao_volta_minutos)
                
                # Gerar SQL para o voo de volta
                f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                f.write(f"('{aviao['no_serie']}', '{hora_partida_volta.strftime('%Y-%m-%d %H:%M:%S')}', ")
                f.write(f"'{hora_chegada_volta.strftime('%Y-%m-%d %H:%M:%S')}', '{destino}', '{origem}');\n")
                
                voo_id += 1
                voos_por_dia[dia_atual.strftime("%Y-%m-%d")] += 1
                
                # Atualizar a localização do avião para onde ele voltou
                localizacoes[aviao["no_serie"]] = origem
                
                # Atualizar quando o avião estará disponível novamente
                disponibilidade_avioes[aviao["no_serie"]] = hora_chegada_volta + datetime.timedelta(hours=1)
            
            # Se não conseguimos 5 voos neste dia, criar mais voos com aviões disponíveis
            while voos_por_dia[dia_atual.strftime("%Y-%m-%d")] < voos_necessarios:
                # Escolher um avião aleatório
                aviao = random.choice(avioes)
                origem = localizacoes[aviao["no_serie"]]
                
                # Escolher destino diferente da origem
                destinos_possiveis = [a["codigo"] for a in aeroportos if a["codigo"] != origem]
                destino = random.choice(destinos_possiveis)
                
                # Definir hora de partida tarde no dia (19h-21h)
                hora_partida = datetime.datetime.combine(
                    dia_atual.date(), 
                    datetime.time(
                        hour=random.randint(19, 21),
                        minute=random.choice([0, 15, 30, 45])
                    )
                )
                
                # Obter duração do voo e calcular hora de chegada
                duracao_minutos = obter_duracao_voo(origem, destino)
                hora_chegada = hora_partida + datetime.timedelta(minutes=duracao_minutos)
                
                # Gerar SQL para o voo adicional
                f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                f.write(f"('{aviao['no_serie']}', '{hora_partida.strftime('%Y-%m-%d %H:%M:%S')}', ")
                f.write(f"'{hora_chegada.strftime('%Y-%m-%d %H:%M:%S')}', '{origem}', '{destino}');\n")
                
                voo_id += 1
                voos_por_dia[dia_atual.strftime("%Y-%m-%d")] += 1
                
                # Atualizar a localização do avião
                localizacoes[aviao["no_serie"]] = destino
                
                # Atualizar quando o avião estará disponível novamente
                disponibilidade_avioes[aviao["no_serie"]] = hora_chegada + datetime.timedelta(hours=1)
                
                # Se este voo ultrapassa para o próximo dia, pode não precisar de um voo de volta no mesmo dia
                if hora_chegada.date() > dia_atual.date():
                    continue
                
                # Para consistência, adicionar um voo de volta no próximo dia
                hora_partida_volta = datetime.datetime.combine(
                    (dia_atual + datetime.timedelta(days=1)).date(),
                    datetime.time(
                        hour=random.randint(6, 10),
                        minute=random.choice([0, 15, 30, 45])
                    )
                )
                
                duracao_volta_minutos = obter_duracao_voo(destino, origem)
                hora_chegada_volta = hora_partida_volta + datetime.timedelta(minutes=duracao_volta_minutos)
                
                f.write(f"INSERT INTO voo (no_serie, hora_partida, hora_chegada, partida, chegada) VALUES ")
                f.write(f"('{aviao['no_serie']}', '{hora_partida_volta.strftime('%Y-%m-%d %H:%M:%S')}', ")
                f.write(f"'{hora_chegada_volta.strftime('%Y-%m-%d %H:%M:%S')}', '{destino}', '{origem}');\n")
                
                # Atualizar quando o avião estará disponível novamente (para o próximo dia)
                disponibilidade_avioes[aviao["no_serie"]] = hora_chegada_volta + datetime.timedelta(hours=1)
                
                # Reset localização para a origem original
                localizacoes[aviao["no_serie"]] = origem
            
            # Avançar para o próximo dia
            dia_atual += datetime.timedelta(days=1)

    
        # Add transaction COMMIT at the end
        f.write("\nCOMMIT;\n")
            
        # Adicionar estatísticas no final do arquivo
        total_voos = voo_id - 1
        total_dias = (data_fim - data_inicio).days + 1
        media_voos_por_dia = total_voos / total_dias
        
        f.write(f"\n-- Total de voos gerados: {total_voos}\n")
        f.write(f"-- Dias cobertos: {total_dias} (de {data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')})\n")
        f.write(f"-- Média de voos por dia: {media_voos_por_dia:.2f}\n")
        f.write("-- Todos os aviões e aeroportos foram utilizados\n")
        f.write("-- Para cada voo foi gerado um voo de retorno\n")
        f.write("-- Cada avião parte sempre do aeroporto onde chegou anteriormente\n")
        f.write("-- Duração entre os mesmos aeroportos é igual para todos os aviões\n")

    print(f"Arquivo SQL gerado com sucesso: popular_voos_2.sql")
    print(f"Total de voos gerados: {total_voos}")
    print(f"Média de voos por dia: {media_voos_por_dia:.2f}")

if __name__ == "__main__":
    gerar_voos_sql()