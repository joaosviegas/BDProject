DROP TABLE IF EXISTS aeroporto CASCADE;
DROP TABLE IF EXISTS aviao CASCADE;
DROP TABLE IF EXISTS assento CASCADE;
DROP TABLE IF EXISTS voo CASCADE;
DROP TABLE IF EXISTS venda CASCADE;
DROP TABLE IF EXISTS bilhete CASCADE;

CREATE TABLE aeroporto(
	codigo CHAR(3) PRIMARY KEY CHECK (codigo ~ '^[A-Z]{3}$'),
	nome VARCHAR(80) NOT NULL,
	cidade VARCHAR(255) NOT NULL,
	pais VARCHAR(255) NOT NULL,
	UNIQUE (nome, cidade)
);

CREATE TABLE aviao(
	no_serie VARCHAR(80) PRIMARY KEY,
	modelo VARCHAR(80) NOT NULL
);

CREATE TABLE assento (
	lugar VARCHAR(3) CHECK (lugar ~ '^[0-9]{1,2}[A-Z]$'),
	no_serie VARCHAR(80) REFERENCES aviao,
	prim_classe BOOLEAN NOT NULL DEFAULT FALSE,
	PRIMARY KEY (lugar, no_serie)
);

CREATE TABLE voo (
	id SERIAL PRIMARY KEY,
	no_serie VARCHAR(80) REFERENCES aviao,
	hora_partida TIMESTAMP,
	hora_chegada TIMESTAMP, 
	partida CHAR(3) REFERENCES aeroporto(codigo),
	chegada CHAR(3) REFERENCES aeroporto(codigo),
	UNIQUE (no_serie, hora_partida),
	UNIQUE (no_serie, hora_chegada),
	UNIQUE (hora_partida, partida, chegada),
	UNIQUE (hora_chegada, partida, chegada),
	CHECK (partida!=chegada),
	CHECK (hora_partida<=hora_chegada)
);

CREATE TABLE venda (
	codigo_reserva SERIAL PRIMARY KEY,
	nif_cliente CHAR(9) NOT NULL,
	balcao CHAR(3) REFERENCES aeroporto(codigo),
	hora TIMESTAMP
);

CREATE TABLE bilhete (
	id SERIAL PRIMARY KEY,
	voo_id INTEGER REFERENCES voo,
	codigo_reserva INTEGER REFERENCES venda,
	nome_passageiro VARCHAR(80),
	preco NUMERIC(7,2) NOT NULL,
	prim_classe BOOLEAN NOT NULL DEFAULT FALSE,
	lugar VARCHAR(3),
	no_serie VARCHAR(80),
	UNIQUE (voo_id, codigo_reserva, nome_passageiro),
	FOREIGN KEY (lugar, no_serie) REFERENCES assento
);

--

CREATE OR REPLACE FUNCTION verificar_checkin_bilhete()
RETURNS TRIGGER AS $$
DECLARE
    voo_no_serie VARCHAR;
    assento_prim BOOLEAN;
BEGIN
    -- Só verifica se estiver a fazer check-in (lugar e no_serie definidos)
    IF NEW.lugar IS NOT NULL AND NEW.no_serie IS NOT NULL THEN

        -- Obter o avião do voo
        SELECT no_serie INTO voo_no_serie
        FROM voo
        WHERE id = NEW.voo_id;

        -- Verificar se o avião do assento é o mesmo do voo
        IF voo_no_serie IS DISTINCT FROM NEW.no_serie THEN
            RAISE EXCEPTION 'Avião do assento (%), não corresponde ao avião do voo (%).',
                NEW.no_serie, voo_no_serie;
        END IF;

        -- Agora que o avião é válido, verificar se o assento existe
        IF NOT EXISTS (
            SELECT 1
            FROM assento
            WHERE lugar = NEW.lugar AND no_serie = NEW.no_serie
        ) THEN
            RAISE EXCEPTION 'O assento (%) não existe no avião %.', NEW.lugar, NEW.no_serie;
        END IF;

        -- Obter se o assento é de 1ª classe
        SELECT prim_classe INTO assento_prim
        FROM assento
        WHERE lugar = NEW.lugar AND no_serie = NEW.no_serie;

        -- Verificar se a classe do bilhete corresponde à do assento
        IF assento_prim IS DISTINCT FROM NEW.prim_classe THEN
            RAISE EXCEPTION 'Classe do bilhete (%), não corresponde à classe do assento (%).',
                NEW.prim_classe, assento_prim;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

DROP TRIGGER IF EXISTS trg_verificar_checkin_bilhete ON bilhete;

CREATE TRIGGER trg_verificar_checkin_bilhete
BEFORE UPDATE ON bilhete
FOR EACH ROW
EXECUTE FUNCTION verificar_checkin_bilhete();

CREATE OR REPLACE FUNCTION verifica_capacidade()
RETURNS TRIGGER AS $$
DECLARE
    capacidade INTEGER;
    ocupados INTEGER;
    serie VARCHAR;
BEGIN
    -- Verifica se ainda há capacidade para o voo na classe do bilhete
    SELECT no_serie INTO serie FROM voo WHERE id = NEW.voo_id;

    SELECT COUNT(*) INTO capacidade
    FROM assento
    WHERE no_serie = serie AND prim_classe = NEW.prim_classe;

    SELECT COUNT(*) INTO ocupados
    FROM bilhete
    WHERE voo_id = NEW.voo_id AND prim_classe = NEW.prim_classe;

    IF ocupados >= capacidade THEN
        RAISE EXCEPTION 'Capacidade esgotada para o voo % na classe %.', NEW.voo_id, NEW.prim_classe;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--

DROP TRIGGER IF EXISTS trg_verifica_capacidade ON bilhete;

CREATE TRIGGER trg_verifica_capacidade
BEFORE INSERT ON bilhete
FOR EACH ROW
EXECUTE FUNCTION verifica_capacidade();


CREATE OR REPLACE FUNCTION validar_bilhete_antes_partida()
RETURNS TRIGGER AS $$
DECLARE
    venda_hora TIMESTAMP;
    partida TIMESTAMP;
BEGIN
    SELECT v.hora_partida, ve.hora INTO partida, venda_hora
    FROM voo v
    JOIN venda ve ON ve.codigo_reserva = NEW.codigo_reserva
    WHERE v.id = NEW.voo_id;

    IF venda_hora >= partida THEN
        RAISE EXCEPTION 'A venda foi feita depois da partida do voo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validar_bilhete_antes_partida ON bilhete;

CREATE TRIGGER trg_validar_bilhete_antes_partida
AFTER INSERT ON bilhete
FOR EACH ROW
EXECUTE FUNCTION validar_bilhete_antes_partida();