-- Popula a tabela assento

-- Airbus A320
DO $$
DECLARE
  fila INT;
  letras CHAR[] := ARRAY['A','B','C','D','E','F'];
  i INT;
  assento VARCHAR(3);
  prim BOOLEAN;
  aviao TEXT;
BEGIN
  FOR fila IN 1..30 LOOP
    FOR i IN 1..array_length(letras, 1) LOOP
      assento := fila::TEXT || letras[i];
      prim := fila <= 3;  -- primeiras 3 filas = 1ª classe
      FOREACH aviao IN ARRAY ARRAY['A320-001','A320-002','A320-003','A320-004','A320-005'] LOOP
        INSERT INTO assento (lugar, no_serie, prim_classe) VALUES (assento, aviao, prim);
      END LOOP;
    END LOOP;
  END LOOP;
END $$;

-- Boeing 737
DO $$
DECLARE
  fila INT;
  letras CHAR[] := ARRAY['A','B','C','D','E','F'];
  i INT;
  assento VARCHAR(3);
  prim BOOLEAN;
  aviao TEXT;
BEGIN
  FOR fila IN 1..31 LOOP
    FOR i IN 1..array_length(letras, 1) LOOP
      assento := fila::TEXT || letras[i];
      prim := fila <= 3;  -- primeiras 3 filas = 1ª classe
      FOREACH aviao IN ARRAY ARRAY['B737-001','B737-002','B737-003','B737-004','B737-005'] LOOP
        INSERT INTO assento (lugar, no_serie, prim_classe) VALUES (assento, aviao, prim);
      END LOOP;
    END LOOP;
  END LOOP;
END $$;

-- Boeing 787
DO $$
DECLARE
  fila INT;
  letras CHAR[] := ARRAY['A','B','C','D','E','F','G','H','J','K'];  -- salta o I
  i INT;
  assento VARCHAR(3);
  prim BOOLEAN;
  aviao TEXT;
BEGIN
  FOR fila IN 1..40 LOOP
    FOR i IN 1..array_length(letras, 1) LOOP
      assento := fila::TEXT || letras[i];
      prim := fila <= 4;  -- primeiras 4 filas = 1ª classe
      FOREACH aviao IN ARRAY ARRAY['B787-001','B787-002'] LOOP
        INSERT INTO assento (lugar, no_serie, prim_classe) VALUES (assento, aviao, prim);
      END LOOP;
    END LOOP;
  END LOOP;
END $$;

