-- Popula a tabela aviao

-- Airbus A320: A320-001 to A320-005
INSERT INTO aviao (no_serie, modelo)
SELECT 'A320-' || LPAD(i::text, 3, '0'), 'Airbus A320'
FROM generate_series(1, 5) AS s(i);

-- Boeing 737: B737-001 to B737-005
INSERT INTO aviao (no_serie, modelo)
SELECT 'B737-' || LPAD(i::text, 3, '0'), 'Boeing 737'
FROM generate_series(1, 5) AS s(i);

-- Boeing 787: B787-001 to B787-002
INSERT INTO aviao (no_serie, modelo)
SELECT 'B787-' || LPAD(i::text, 3, '0'), 'Boeing 787'
FROM generate_series(1, 2) AS s(i);
