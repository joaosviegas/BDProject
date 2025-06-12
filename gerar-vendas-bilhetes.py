import random
import datetime
from faker import Faker
from collections import defaultdict

# Initialize Faker with multiple locales
fake = Faker(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])

# Configuration
OUTPUT_FILE = "vendas_bilhetes.sql"
CHECKIN_LIMIT_DATE = datetime.datetime(2025, 6, 17)
AIRPORTS = ['LIS', 'OPO', 'FAO', 'BJZ', 'MAD', 'BCN', 'CDG', 'ZRH', 'AMS', 'LHR', 'LGW', 'MXP', 'LIN']

def load_seats():
    """Load seat information from assentos.txt"""
    print("Reading seat information...")
    seats_by_airplane = defaultdict(list)
    first_class_seats = defaultdict(list)
    regular_seats = defaultdict(list)
    
    with open('assentos.txt', 'r') as file:
        for line in file:
            if line.startswith('//'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                seat, airplane, is_first_class = parts
                seats_by_airplane[airplane].append(seat)
                if is_first_class.lower() == 'true':
                    first_class_seats[airplane].append(seat)
                else:
                    regular_seats[airplane].append(seat)
    
    return seats_by_airplane, first_class_seats, regular_seats

def load_flights():
    """Load flight information from voos.txt"""
    print("Reading flight information...")
    flights = []
    
    with open('voos.txt', 'r') as file:
        for line in file:
            if line.startswith('//'):
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 6:
                try:
                    flight_id = int(parts[0])
                    airplane = parts[1]
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
    
    return sorted(flights, key=lambda x: x['departure_time'])

def generate_vat():
    """Generate a 9-digit VAT number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(9)])

def calculate_occupancy(departure_time):
    """Calculate realistic occupancy based on departure date"""
    current_date = datetime.datetime(2025, 6, 5)
    
    if departure_time < current_date:
        # Past flights: high occupancy
        return random.uniform(0.85, 0.99)
    else:
        # Future flights: variable occupancy
        return random.uniform(0.60, 0.90)

def get_available_seat(used_seats, airplane_seats, is_first_class):
    """Get an available seat of the specified class"""
    available_seats = [seat for seat in airplane_seats if seat not in used_seats]
    if not available_seats:
        return None
    
    seat = random.choice(available_seats)
    used_seats.add(seat)
    return seat

def generate_sale_data():
    """Generate sale data (NIF, counter, locale)"""
    locale = random.choice(['pt_PT', 'es_ES', 'fr_FR', 'en_GB', 'it_IT', 'de_DE'])
    return {
        'nif': generate_vat(),
        'counter': random.choice(AIRPORTS),
        'locale': locale
    }

def generate_sale_time(departure_time):
    """Generate a realistic sale time before departure"""
    days_before = random.randint(1, 90)
    sale_time = departure_time - datetime.timedelta(days=days_before)
    return max(sale_time, departure_time - datetime.timedelta(days=1))

def write_sale(f, sale_data, sale_time):
    """Write a sale INSERT statement"""
    f.write(f"INSERT INTO venda (nif_cliente, balcao, hora)\n")
    f.write(f"VALUES ('{sale_data['nif']}', '{sale_data['counter']}', '{sale_time.strftime('%Y-%m-%d %H:%M:%S')}');\n\n")

def write_tickets(f, tickets):
    """Write ticket INSERT statements"""
    if not tickets:
        return
    
    f.write("INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, lugar, no_serie)\nVALUES\n")
    f.write(",\n".join(tickets))
    f.write(";\n\n")

def generate_tickets_for_flight(flight, first_class_seats, regular_seats, seats_by_airplane):
    """Generate all tickets for a single flight"""
    flight_id = flight['id']
    airplane = flight['airplane']
    departure_time = flight['departure_time']
    
    # Calculate how many seats to fill
    total_seats = len(seats_by_airplane[airplane])
    occupancy = calculate_occupancy(departure_time)
    seats_to_fill = max(2, int(total_seats * occupancy))  # Minimum 2 seats
    
    # Ensure we have seats of both classes
    first_class_count = min(len(first_class_seats[airplane]), max(1, seats_to_fill // 10))
    regular_count = min(len(regular_seats[airplane]), seats_to_fill - first_class_count)
    
    # Track used seats for this flight
    used_seats = set()
    
    # Generate sales with tickets
    tickets_remaining = first_class_count + regular_count
    first_class_remaining = first_class_count
    regular_remaining = regular_count
    
    while tickets_remaining > 0:
        # Generate sale data
        sale_data = generate_sale_data()
        sale_time = generate_sale_time(departure_time)
        
        # Determine tickets in this sale (1-4 tickets per sale)
        tickets_in_sale = min(tickets_remaining, random.choices([1, 2, 3, 4], weights=[0.3, 0.4, 0.2, 0.1])[0])
        
        # Generate tickets for this sale
        tickets = []
        for _ in range(tickets_in_sale):
            # Determine class (prioritize first class if needed)
            if first_class_remaining > 0 and (regular_remaining == 0 or random.random() < 0.3):
                is_first_class = True
                seat = get_available_seat(used_seats, first_class_seats[airplane], True)
                first_class_remaining -= 1
            elif regular_remaining > 0:
                is_first_class = False
                seat = get_available_seat(used_seats, regular_seats[airplane], False)
                regular_remaining -= 1
            else:
                break
            
            if not seat:
                break
            
            # Generate passenger and price
            passenger_name = fake[sale_data['locale']].name().replace("'", "")
            price = round(random.uniform(100, 1200), 2) if is_first_class else round(random.uniform(80, 350), 2)
            
            # Handle check-in (seat assignment)
            if departure_time > CHECKIN_LIMIT_DATE:
                # No check-in for flights after limit date
                lugar_sql = 'NULL'
                no_serie_sql = 'NULL'
            else:
                lugar_sql = f"'{seat}'"
                no_serie_sql = f"'{airplane}'"
            
            tickets.append(f"({flight_id}, currval('venda_codigo_reserva_seq'), '{passenger_name}', {price}, {'TRUE' if is_first_class else 'FALSE'}, {lugar_sql}, {no_serie_sql})")
            tickets_remaining -= 1
        
        # Write sale and tickets if we have any
        if tickets:
            yield sale_data, sale_time, tickets


def main():
    # Load data
    seats_by_airplane, first_class_seats, regular_seats = load_seats()
    flights = load_flights()
    
    print(f"Found {len(set(airplane for airplane in seats_by_airplane.keys()))} airplanes")
    print(f"Loaded {len(flights)} flights")
    
    # Coletar todas as vendas e bilhetes
    all_sales = []
    all_tickets = []
    sale_index = 1  # Simulando a sequência de códigos de reserva
    
    # Conjuntos para detectar duplicados
    sales_set = set()  # (nif, balcao, hora)
    tickets_set = set()  # (voo_id, nome_passageiro, prim_classe, lugar)
    passengers_by_sale = {}
    
    # Process each flight
    for flight in flights:
        print(f"Processing flight {flight['id']} ({flight['departure_time'].strftime('%Y-%m-%d')})")
        
        for sale_data, sale_time, tickets in generate_tickets_for_flight(
            flight, first_class_seats, regular_seats, seats_by_airplane
        ):
            # Verificar duplicação de venda
            sale_key = (sale_data['nif'], sale_data['counter'], sale_time.strftime('%Y-%m-%d %H:%M:%S'))
            if sale_key in sales_set:
                continue
                
            # Adicionar venda
            sales_set.add(sale_key)
            all_sales.append((sale_data['nif'], sale_data['counter'], sale_time.strftime('%Y-%m-%d %H:%M:%S')))
            
            # Adicionar bilhetes verificando duplicações
            for ticket_str in tickets:
                # Extrair dados do bilhete da string SQL
                ticket_parts = ticket_str.strip("()").split(", ")
                flight_id = ticket_parts[0]
                passenger = ticket_parts[2].strip("'")
                is_first = ticket_parts[4]
                seat = ticket_parts[5]

                if sale_index not in passengers_by_sale:
                    passengers_by_sale[sale_index] = set()

                if passenger in passengers_by_sale[sale_index]:
                    continue  # Pula bilhetes com nomes duplicados na mesma venda
                    
                passengers_by_sale[sale_index].add(passenger)

                # Verificar duplicação
                ticket_key = (flight_id, passenger, is_first, seat)
                # Se o bilhete já foi adicionado, não adiciona novamente
                if ticket_key in tickets_set:
                    continue
                # Adicionar bilhete ao conjunto de tickets
                tickets_set.add(ticket_key)
                
                # Substituir currval pela referência ao índice
                modified_ticket = ticket_str.replace("currval('venda_codigo_reserva_seq')", str(sale_index))
                all_tickets.append(modified_ticket)
            
            sale_index += 1
    
    # Escrever no arquivo em batch
    with open(OUTPUT_FILE, 'w') as f:

        f.write("BEGIN;\n\n")
        f.write("-- Generated Sales and Tickets for Aviation Database\n")
        f.write("-- Generated on: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
        
        # Escrever todas as vendas em batches
        batch_size = 1000
        for i in range(0, len(all_sales), batch_size):
            batch = all_sales[i:i+batch_size]
            f.write("INSERT INTO venda (nif_cliente, balcao, hora) VALUES\n")
            values = []
            for sale in batch:
                values.append(f"('{sale[0]}', '{sale[1]}', '{sale[2]}')")
            f.write(",\n".join(values) + ";\n\n")
        
        # Escrever todos os bilhetes em batches
        for i in range(0, len(all_tickets), batch_size):
            batch = all_tickets[i:i+batch_size]
            if batch:
                f.write("INSERT INTO bilhete (voo_id, codigo_reserva, nome_passageiro, preco, prim_classe, lugar, no_serie) VALUES\n")
                f.write(",\n".join(batch) + ";\n\n")
        
        f.write(f"-- Generated {len(all_sales)} sales and {len(all_tickets)} tickets\n")
        f.write("COMMIT;\n")
    
    print(f"\nGenerated {len(all_sales)} sales and {len(all_tickets)} tickets")
    print(f"Data written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()