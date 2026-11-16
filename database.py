import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Таблица Книги
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        shifr TEXT PRIMARY KEY,
        author TEXT NOT NULL,
        title TEXT NOT NULL,
        publisher TEXT NOT NULL,
        year INTEGER NOT NULL
    );
    """)

    # 2. Таблица Библиотеки
    cur.execute("""
    CREATE TABLE IF NOT EXISTS libraries (
        number INTEGER PRIMARY KEY,
        address TEXT NOT NULL,
        phone TEXT NOT NULL
    );
    """)

    # 3. Таблица Экземпляры
    cur.execute("""
    CREATE TABLE IF NOT EXISTS copies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lib_number INTEGER NOT NULL,
        book_shifr TEXT NOT NULL,
        hall TEXT NOT NULL,
        FOREIGN KEY (lib_number) REFERENCES libraries(number) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (book_shifr) REFERENCES books(shifr) ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # Начальные данные Варианта 17
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        books_data = [
            ('B001', 'Пушкин А.С.', 'Евгений Онегин', 'Эксмо', 2020),
            ('B002', 'Толстой Л.Н.', 'Война и мир', 'АСТ', 2018),
            ('B003', 'Достоевский Ф.М.', 'Преступление и наказание', 'Питер', 2019),
            ('B004', 'Булгаков М.А.', 'Мастер и Маргарита', 'АСТ', 2015),
            ('B005', 'Гоголь Н.В.', 'Мертвые души', 'Эксмо', 2021),
            ('B006', 'Чехов А.П.', 'Вишневый сад', 'Наука', 2017),
        ]
        cur.executemany("INSERT INTO books (shifr, author, title, publisher, year) VALUES (?, ?, ?, ?, ?)", books_data)

    cur.execute("SELECT COUNT(*) FROM libraries")
    if cur.fetchone()[0] == 0:
        libs_data = [
            (1, 'ул. Ленина, д.5', '123-45-67'),
            (2, 'ул. Пушкина, д.10', '234-56-78'),
            (3, 'пр. Машерова, д.15', '345-67-89'),
        ]
        cur.executemany("INSERT INTO libraries (number, address, phone) VALUES (?, ?, ?)", libs_data)

    cur.execute("SELECT COUNT(*) FROM copies")
    if cur.fetchone()[0] == 0:
        copies_data = [
            (1, 'B001', 'Зал художественной литературы'),
            (1, 'B002', 'Зал классики'),
            (2, 'B001', 'Зал поэзии'),
            (2, 'B003', 'Зал прозы'),
            (3, 'B004', 'Зал редких изданий'),
            (3, 'B005', 'Читальный зал №1'),
            (1, 'B006', 'Абонементный зал'),
        ]
        cur.executemany("INSERT INTO copies (lib_number, book_shifr, hall) VALUES (?, ?, ?)", copies_data)

    conn.commit()
    conn.close()

def get_libraries_dict():
    conn = get_connection()
    rows = conn.execute("SELECT number, address FROM libraries ORDER BY number").fetchall()
    conn.close()
    return {r["number"]: f"Филиал №{r['number']} ({r['address']})" for r in rows}

def get_books_dict():
    conn = get_connection()
    rows = conn.execute("SELECT shifr, title, author FROM books ORDER BY shifr").fetchall()
    conn.close()
    return {r["shifr"]: f"{r['shifr']} — {r['title']} ({r['author']})" for r in rows}

def get_db_stats():
    conn = get_connection()
    b_cnt = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    l_cnt = conn.execute("SELECT COUNT(*) FROM libraries").fetchone()[0]
    c_cnt = conn.execute("SELECT COUNT(*) FROM copies").fetchone()[0]
    conn.close()
    return {"books": b_cnt, "libraries": l_cnt, "copies": c_cnt}

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
    print("Stats:", get_db_stats())
