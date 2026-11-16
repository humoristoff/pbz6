import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sklad.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Таблица Склады
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sklady (
        kod_sklada INTEGER PRIMARY KEY AUTOINCREMENT,
        adres TEXT NOT NULL,
        telefon TEXT NOT NULL,
        firma TEXT NOT NULL
    );
    """)

    # 2. Таблица Производители
    cur.execute("""
    CREATE TABLE IF NOT EXISTS proizvoditeli (
        kod_proiz INTEGER PRIMARY KEY AUTOINCREMENT,
        name_proiz TEXT NOT NULL,
        adres_proiz TEXT NOT NULL,
        telefon_proiz TEXT NOT NULL,
        strana TEXT NOT NULL
    );
    """)

    # 3. Таблица Товары
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tovary (
        kod_tovara INTEGER PRIMARY KEY AUTOINCREMENT,
        kod_sklada INTEGER NOT NULL,
        kod_proiz INTEGER NOT NULL,
        name_t TEXT NOT NULL,
        edizmer TEXT NOT NULL,
        kol INTEGER NOT NULL,
        FOREIGN KEY (kod_sklada) REFERENCES sklady(kod_sklada) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (kod_proiz) REFERENCES proizvoditeli(kod_proiz) ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # Начальные данные Варианта 15 («Склад товаров»)
    cur.execute("SELECT COUNT(*) FROM sklady")
    if cur.fetchone()[0] == 0:
        sklady_data = [
            ('ул. Ленина, 10', '8-800-555-01-01', 'ООО "Склад-Сервис"'),
            ('пр. Победы, 25', '8-800-555-02-02', 'ЗАО "Логистик-Центр"'),
            ('ул. Советская, 5', '8-800-555-03-03', 'ООО "Хранение+"'),
            ('ул. Мира, 12', '8-800-555-05-05', 'ООО "Логистика+"'),
            ('пер. Садовый, 3', '8-800-555-06-06', 'ЗАО "Складской комплекс"')
        ]
        cur.executemany("INSERT INTO sklady (adres, telefon, firma) VALUES (?, ?, ?)", sklady_data)

    cur.execute("SELECT COUNT(*) FROM proizvoditeli")
    if cur.fetchone()[0] == 0:
        proiz_data = [
            ('ООО "ТехноПром"', 'г. Москва', '8-495-111-11-11', 'Россия'),
            ('Bosch GmbH', 'г. Штутгарт', '+49-711-222-22', 'Германия'),
            ('ООО "СтройМир"', 'г. Санкт-Петербург', '8-812-333-33-33', 'Россия'),
            ('Makita Corp.', 'г. Токио', '+81-3-1234-5678', 'Япония'),
            ('ООО "Электроника"', 'г. Казань', '8-843-777-77-77', 'Россия')
        ]
        cur.executemany("INSERT INTO proizvoditeli (name_proiz, adres_proiz, telefon_proiz, strana) VALUES (?, ?, ?, ?)", proiz_data)

    cur.execute("SELECT COUNT(*) FROM tovary")
    if cur.fetchone()[0] == 0:
        tovary_data = [
            (1, 1, 'Дрель электрическая', 'шт', 50),
            (1, 2, 'Болгарка (УШМ)', 'шт', 30),
            (2, 3, 'Цемент', 'мешок', 100),
            (3, 1, 'Шуруповерт', 'шт', 25),
            (3, 2, 'Перфоратор', 'шт', 15),
            (4, 4, 'Шлифмашина угловая', 'шт', 20),
            (5, 5, 'Мультиметр цифровой', 'шт', 45)
        ]
        cur.executemany("INSERT INTO tovary (kod_sklada, kod_proiz, name_t, edizmer, kol) VALUES (?, ?, ?, ?, ?)", tovary_data)

    conn.commit()
    conn.close()

def get_sklady_dict():
    conn = get_connection()
    rows = conn.execute("SELECT kod_sklada, firma, adres FROM sklady ORDER BY kod_sklada").fetchall()
    conn.close()
    return {r["kod_sklada"]: f"{r['kod_sklada']} — {r['firma']} ({r['adres']})" for r in rows}

def get_proizvoditeli_dict():
    conn = get_connection()
    rows = conn.execute("SELECT kod_proiz, name_proiz, strana FROM proizvoditeli ORDER BY kod_proiz").fetchall()
    conn.close()
    return {r["kod_proiz"]: f"{r['kod_proiz']} — {r['name_proiz']} ({r['strana']})" for r in rows}

def get_db_stats():
    conn = get_connection()
    sklady_cnt = conn.execute("SELECT COUNT(*) FROM sklady").fetchone()[0]
    proiz_cnt = conn.execute("SELECT COUNT(*) FROM proizvoditeli").fetchone()[0]
    tovary_cnt = conn.execute("SELECT COUNT(*) FROM tovary").fetchone()[0]
    total_kol = conn.execute("SELECT COALESCE(SUM(kol), 0) FROM tovary").fetchone()[0]
    conn.close()
    return {
        "sklady": sklady_cnt,
        "proizvoditeli": proiz_cnt,
        "tovary": tovary_cnt,
        "total_kol": total_kol
    }

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
    print("Stats:", get_db_stats())
