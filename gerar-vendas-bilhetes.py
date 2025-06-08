import random
import datetime
from faker import Faker
from collections import defaultdict
import sys

# Initialize Faker with multiple locales for international names
fake = Faker(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])

# Output file for SQL inserts
output_file = "vendas_bilhetes.sql"

# Read seat information from assentos.txt
print("Reading seat information...")
airplanes = set()
seats_by_airplane = defaultdict(list)
first_class_seats = defaultdict(list)
regular_seats = defaultdict(list)

with open('assentos.txt', 'r') as file:
    for line in file:
        if line.startswith('//'):  # Skip comment lines
            continue
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            seat, airplane, is_first_class = parts
            airplanes.add(airplane)
            seats_by_airplane[airplane].append(seat)
            if is_first_class.lower() == 'true':
                first_class_seats[airplane].append(seat)
            else:
                regular_seats[airplane].append(seat)

print(f"Found {len(airplanes)} airplanes with seats")

# Read flight information from voos.txt
print("Reading flight information...")
flights = []

with open('voos.txt', 'r') as file:
    for line in file:
        if line.startswith('//'):  # Skip comment lines
            continue
        parts = line.strip().split('\t')
        if len(parts) >= 6:
            try:
                flight_id = int(parts[0])
                airplane = parts[1]
                
                # Fix: Handle the milliseconds in datetime format
                departure_time = datetime.datetime.strptime(parts[2].split('.')[0], '%Y-%m-%d %H:%M:%S')
                arrival_time = datetime.datetime.strptime(parts[3].split('.')[0], '%Y-%m-%d %H:%M:%S')
                
                departure_airport = parts[4]
                arrival_airport = parts[5]
                
                flights.append({
                    'id': flight_id,
                    'airplane': airplane,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'departure_airport': departure_airport,
                    'arrival_airport': arrival_airport
                })
            except ValueError as e:
                print(f"Error parsing flight: {line.strip()}")
                print(f"Error details: {e}")

# Sort flights by departure time
flights.sort(key=lambda x: x['departure_time'])
print(f"Loaded {len(flights)} flights")

# Mock current date for the simulation (June 5, 2025)
current_date = datetime.datetime(2025, 6, 5)

# List of airports for counter locations
airports = ['LIS', 'OPO', 'FAO', 'BJZ', 'MAD', 'BCN', 'CDG', 'ZRH', 'AMS', 'LHR', 'LGW', 'MXP', 'LIN']

# Dict to track assigned seats
assigned_seats = defaultdict(set)

# Function to generate country-specific tax IDs (VAT/NIF)
def generate_vat(country='PT'):
    if country == 'PT':  # Portugal: 9 digits
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    elif country == 'ES':  # Spain
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    elif country == 'FR':  # France
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    elif country == 'GB':  # UK
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    elif country == 'IT':  # Italy
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    elif country == 'DE':  # Germany
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])
    else:
        return ''.join([str(random.randint(0, 9)) for _ in range(9)])

# Function to get a random available seat
def get_available_seat(flight_id, airplane, is_first_class):
    if is_first_class:
        available_seats = [seat for seat in first_class_seats[airplane] 
                         if seat not in assigned_seats[flight_id]]
        if not available_seats:
            return None
    else:
        available_seats = [seat for seat in regular_seats[airplane] 
                         if seat not in assigned_seats[flight_id]]
        if not available_seats:
            return None
    
    seat = random.choice(available_seats)
    assigned_seats[flight_id].add(seat)
    return seat

# Generate sales and tickets
target_sales = 10000
target_tickets = 30000
sale_id = 1
ticket_count = 0
flights_with_first_class = set()
flights_with_regular_class = set()

with open(output_file, 'w') as f:
    f.write("BEGIN;\n\n")

    print("First pass: Ensuring every flight has at least one ticket of each class...")
    for flight in flights:
        flight_id = flight['id']
        airplane = flight['airplane']
        departure_time = flight['departure_time']

        for is_first_class in [True, False]:
            # Só tenta se houver lugares dessa classe
            seats_list = first_class_seats[airplane] if is_first_class else regular_seats[airplane]
            if not seats_list:
                continue

            # Só tenta se ainda não tem bilhete dessa classe para este voo
            already_has = (flight_id in flights_with_first_class) if is_first_class else (flight_id in flights_with_regular_class)
            if already_has:
                continue

            locale = random.choice(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])
            country_code = locale.split('_')[1]
            nif = generate_vat(country_code)
            counter = random.choice(airports)
            days_before = random.randint(1, 60)
            sale_time = departure_time - datetime.timedelta(days=days_before)
            if sale_time >= departure_time:
                sale_time = departure_time - datetime.timedelta(days=1)

            f.write(f"INSERT INTO venda (nif_cliente, balcao, hora)\n")
            f.write(f"VALUES ('{nif}', '{counter}', '{sale_time.strftime('%Y-%m-%d %H:%M:%S')}');\n\n")

            used_names = set()
            passenger_name = fake[locale].name().replace("'", "")
            while passenger_name in used_names:
                passenger_name = fake[locale].name().replace("'", "")
            used_names.add(passenger_name)

            seat = get_available_seat(flight_id, airplane, is_first_class)
            if not seat:
                continue

            price = round(random.uniform(400, 1200), 2) if is_first_class else round(random.uniform(80, 350), 2)
            f.write(
                "INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, lugar, no_serie)\n"
                f"VALUES ({flight_id}, currval('venda_codigo_reserva_seq'), '{passenger_name}', {price}, {'TRUE' if is_first_class else 'FALSE'}, '{seat}', '{airplane}');\n\n"
            )

            ticket_count += 1
            if is_first_class:
                flights_with_first_class.add(flight_id)
            else:
                flights_with_regular_class.add(flight_id)

            sale_id += 1

    print(f"After first pass: {ticket_count} tickets, {len(flights_with_first_class)} flights with first class, {len(flights_with_regular_class)} flights with regular class")

    f.write("-- Generated Sales and Tickets for Aviation Database\n")
    f.write("-- Generated on: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
    
    # Process flights in chronological order
    print("Generating tickets for flights chronologically...")
    for flight in flights:
        flight_id = flight['id']
        airplane = flight['airplane']
        departure_time = flight['departure_time']
        is_past_flight = departure_time < current_date
        
        # Calculate target occupancy (higher for past flights)
        seats_total = len(seats_by_airplane[airplane])
        occupancy_target = random.uniform(0.75, 0.98) if is_past_flight else random.uniform(0.65, 0.90)
        seats_to_fill = int(seats_total * occupancy_target)
        
        # Ensure at least some first class and regular seats are filled
        first_class_seats_total = len(first_class_seats[airplane])
        regular_seats_total = len(regular_seats[airplane])
        
        # Ensure every flight has at least some first class and regular tickets
        first_class_min = min(2, first_class_seats_total)  # At least 2 first class if available
        regular_min = min(5, regular_seats_total)          # At least 5 regular if available
        
        # Calculate how many seats of each class to fill
        first_class_to_fill = max(first_class_min, 
                                int(first_class_seats_total * occupancy_target))
        regular_to_fill = max(regular_min, 
                            int(regular_seats_total * occupancy_target))
        
        # Limit to available seats
        first_class_to_fill = min(first_class_to_fill, first_class_seats_total)
        regular_to_fill = min(regular_to_fill, regular_seats_total)
        
        # Group tickets by sales (1-3 tickets per sale)
        tickets_to_generate = first_class_to_fill + regular_to_fill
        sales_for_flight = []
        
        # Distribute tickets to sales (1-3 tickets per sale)
        remaining_tickets = tickets_to_generate
        while remaining_tickets > 0:
            # For the last few tickets, ensure each gets a sale
            if remaining_tickets <= 3:
                tickets_in_sale = remaining_tickets
            else:
                tickets_in_sale = random.choices(
                    [1, 2, 3, 4, 5], 
                    weights=[0.01, 0.04, 0.15, 0.30, 0.50],  # Most sales have 5
                    k=1
                )[0]
            
            tickets_in_sale = min(tickets_in_sale, remaining_tickets)
            sales_for_flight.append(tickets_in_sale)
            remaining_tickets -= tickets_in_sale
        
        # Agora gera as vendas e bilhetes (mais eficiente, 1 insert por venda, múltiplos bilhetes)
        for tickets_in_sale in sales_for_flight:
            if ticket_count >= target_tickets:
                continue

            locale = random.choice(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])
            country_code = locale.split('_')[1]
            nif = generate_vat(country_code)
            counter = random.choice(airports)
            days_before = random.randint(1, 60)
            sale_time = departure_time - datetime.timedelta(days=days_before)
            if sale_time >= departure_time:
                sale_time = departure_time - datetime.timedelta(days=1)

            # Gera a venda
            f.write(f"INSERT INTO venda (nif_cliente, balcao, hora)\n")
            f.write(f"VALUES ('{nif}', '{counter}', '{sale_time.strftime('%Y-%m-%d %H:%M:%S')}');\n\n")

            # Gera os bilhetes desta venda (garante pelo menos 1 bilhete por venda)
            bilhetes = []
            for _ in range(tickets_in_sale):
                is_first_class = False
                # Alterna entre classes se possível
                if first_class_to_fill > 0:
                    is_first_class = True
                    first_class_to_fill -= 1
                elif regular_to_fill > 0:
                    is_first_class = False
                    regular_to_fill -= 1
                else:
                    continue

                passenger_name = fake[locale].name().replace("'", "")
                seat = get_available_seat(flight_id, airplane, is_first_class)
                if not seat and is_first_class:
                    is_first_class = False
                    seat = get_available_seat(flight_id, airplane, False)
                if not seat:
                    continue

                price = round(random.uniform(400, 1200), 2) if is_first_class else round(random.uniform(80, 350), 2)
                bilhetes.append(
                    f"({flight_id}, currval('venda_codigo_reserva_seq'), '{passenger_name}', {price}, {'TRUE' if is_first_class else 'FALSE'}, '{seat}', '{airplane}')"
                )
                ticket_count += 1
                if is_first_class:
                    flights_with_first_class.add(flight_id)
                else:
                    flights_with_regular_class.add(flight_id)

            # Garante pelo menos 1 bilhete por venda
            if len(bilhetes) == 0:
                is_first_class = regular_to_fill == 0
                passenger_name = fake[locale].name().replace("'", "")
                seat = get_available_seat(flight_id, airplane, is_first_class)
                if not seat and is_first_class:
                    is_first_class = False
                    seat = get_available_seat(flight_id, airplane, False)
                if seat:
                    price = round(random.uniform(400, 1200), 2) if is_first_class else round(random.uniform(80, 350), 2)
                    bilhetes.append(
                        f"({flight_id}, currval('venda_codigo_reserva_seq'), '{passenger_name}', {price}, {'TRUE' if is_first_class else 'FALSE'}, '{seat}', '{airplane}')"
                    )
                    ticket_count += 1
                    if is_first_class:
                        flights_with_first_class.add(flight_id)
                    else:
                        flights_with_regular_class.add(flight_id)

            if bilhetes:
                f.write(
                    "INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, lugar, no_serie)\nVALUES\n"
                    + ",\n".join(bilhetes) + ";\n\n"
                )
            sale_id += 1

            if ticket_count >= target_tickets:
                break
    
    # If we haven't reached our target tickets, process more flights
    if ticket_count < target_tickets:
        print(f"Only generated {ticket_count}/{target_tickets} tickets, adding more tickets...")
        
        # Identify flights with available seats
        available_flights = []
        for flight in flights:
            flight_id = flight['id']
            airplane = flight['airplane']
            total_seats = len(seats_by_airplane[airplane])
            used_seats = len(assigned_seats[flight_id])
            
            if used_seats < total_seats:
                # This flight has available seats
                available_flights.append({
                    'flight': flight,
                    'available': total_seats - used_seats
                })
        
        # Sort by number of available seats (most first)
        available_flights.sort(key=lambda x: x['available'], reverse=True)
        
        # Keep adding tickets until we reach our target
        for flight_data in available_flights:
            if ticket_count >= target_tickets:
                break
                
            flight = flight_data['flight']
            flight_id = flight['id']
            airplane = flight['airplane']
            departure_time = flight['departure_time']
            
            # How many more tickets to add for this flight (up to 80% of available)
            tickets_to_add = min(
                int(flight_data['available'] * 0.8), 
                target_tickets - ticket_count
            )
            
            if tickets_to_add <= 0:
                continue
            
            # Create sales and tickets
            while tickets_to_add > 0:
                # Decide how many tickets in this sale
                tickets_in_sale = min(tickets_to_add, random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.01, 0.04, 0.15, 0.30, 0.50],  # Same weights as above
                    k=1
                )[0])
                
                # Generate sale
                locale = random.choice(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])
                country_code = locale.split('_')[1]
                nif = generate_vat(country_code)
                counter = random.choice(airports)
                
                days_before = random.randint(1, 60)
                sale_time = departure_time - datetime.timedelta(days=days_before)
                
                f.write(f"INSERT INTO venda (nif_cliente, balcao, hora)\n")
                f.write(f"VALUES ('{nif}', '{counter}', '{sale_time.strftime('%Y-%m-%d %H:%M:%S')}');\n\n")
                
                # Generate tickets for this sale
                for _ in range(tickets_in_sale):
                    # Decide class (mostly regular)
                    is_first_class = random.random() < 0.2
                    
                    # Generate passenger name
                    passenger_name = fake[locale].name()
                    passenger_name = passenger_name.replace("'", "")
                    
                    # Get seat
                    seat = get_available_seat(flight_id, airplane, is_first_class)
                    if not seat and is_first_class:
                        # Try regular class if first class is full
                        is_first_class = False
                        seat = get_available_seat(flight_id, airplane, False)
                    if not seat:
                        continue  # Skip if still no seats available
                    
                    # Price based on class
                    price = round(random.uniform(400, 1200), 2) if is_first_class else round(random.uniform(80, 350), 2)
                    
                    # Write ticket insert
                    field_name = "nome_passageiro"  # Correct field name
                    f.write(f"INSERT INTO bilhete (voo_id, codigo_reserva, {field_name}, preco, prim_classe, lugar, no_serie)\n")
                    f.write(f"VALUES ({flight_id}, currval('venda_codigo_reserva_seq'), '{passenger_name}', {price}, {'TRUE' if is_first_class else 'FALSE'}, '{seat}', '{airplane}');\n\n")
                    
                    ticket_count += 1
                    if is_first_class:
                        flights_with_first_class.add(flight_id)
                    else:
                        flights_with_regular_class.add(flight_id)
                
                sale_id += 1
                tickets_to_add -= tickets_in_sale

    f.write(f"-- Generated {sale_id-1} sales and {ticket_count} tickets\n")
    f.write(f"-- Flights with first class tickets: {len(flights_with_first_class)}\n")
    f.write(f"-- Flights with regular class tickets: {len(flights_with_regular_class)}\n")
    
    # Check if all flights have both classes of tickets
    all_flights = set(flight['id'] for flight in flights)
    missing_first_class = all_flights - flights_with_first_class
    missing_regular_class = all_flights - flights_with_regular_class
    
    if missing_first_class:
        f.write(f"-- Warning: {len(missing_first_class)} flights are missing first class tickets\n")
    
    if missing_regular_class:
        f.write(f"-- Warning: {len(missing_regular_class)} flights are missing regular class tickets\n")
        
    f.write("\nCOMMIT;\n")

print(f"Generated {sale_id-1} sales and {ticket_count} tickets")
print(f"Flights with first class tickets: {len(flights_with_first_class)}")
print(f"Flights with regular class tickets: {len(flights_with_regular_class)}")
print(f"Generated data written to {output_file}")