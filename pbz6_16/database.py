import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library16.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 1. Таблица Книги (books)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        shifr TEXT PRIMARY KEY,
        author TEXT NOT NULL,
        title TEXT NOT NULL,
        publisher TEXT NOT NULL,
        year INTEGER NOT NULL
    );
    """)

    # 2. Таблица Читатели (readers)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS readers (
        reader_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        education TEXT NOT NULL
    );
    """)

    # 3. Таблица Выдача книг на руки (loans)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reader_id INTEGER NOT NULL,
        shifr TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        return_date TEXT NOT NULL,
        FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (shifr) REFERENCES books(shifr) ON UPDATE CASCADE ON DELETE CASCADE
    );
    """)

    # Первичное наполнение данными для Варианта 16
    cur.execute("SELECT COUNT(*) FROM books")
    if cur.fetchone()[0] == 0:
        books_data = [
            ('КН-101', 'Оруэлл Дж.', '1984', 'Секер и Варбург', 1949),
            ('КН-102', 'Хемингуэй Э.', 'Старик и море', 'Скрибнер', 1952),
            ('КН-103', 'Кафка Ф.', 'Процесс', 'Die Schmiede', 1925),
            ('КН-104', 'Булгаков М.А.', 'Мастер и Маргарита', 'YMCA Press', 1967),
            ('КН-105', 'Достоевский Ф.М.', 'Преступление и наказание', 'Русский вестник', 1866),
            ('КН-106', 'Толстой Л.Н.', 'Война и мир', 'Русский вестник', 1869),
            ('КН-107', 'Ремарк Э.М.', 'Три товарища', 'Gyldendal', 1936),
            ('КН-108', 'Брэдбери Р.', '451 градус по Фаренгейту', 'Ballantine Books', 1953),
        ]
        cur.executemany("INSERT INTO books (shifr, author, title, publisher, year) VALUES (?, ?, ?, ?, ?)", books_data)

    cur.execute("SELECT COUNT(*) FROM readers")
    if cur.fetchone()[0] == 0:
        readers_data = [
            (501, 'Смирнов А.А.', 'г. Брест, ул. Пушкинская, 15', '+375 (29) 123-45-67', 'высшее'),
            (502, 'Кузнецова М.И.', 'г. Брест, ул. Советская, 42', '+375 (29) 234-56-78', 'среднее'),
            (503, 'Волков Д.С.', 'г. Брест, ул. Мицкевича, 9', '+375 (29) 345-67-89', 'высшее'),
            (504, 'Морозова Е.В.', 'г. Брест, бул. Космонавтов, 21', '+375 (33) 456-78-90', 'студент'),
            (505, 'Павлов К.Н.', 'г. Брест, ул. Московская, 108', '+375 (29) 567-89-01', 'бакалавр'),
            (506, 'Лебедева О.А.', 'г. Брест, ул. Ленина, 33', '+375 (44) 678-90-12', 'магистр'),
        ]
        cur.executemany("INSERT INTO readers (reader_id, full_name, address, phone, education) VALUES (?, ?, ?, ?, ?)", readers_data)

    cur.execute("SELECT COUNT(*) FROM loans")
    if cur.fetchone()[0] == 0:
        loans_data = [
            (501, 'КН-101', '2026-09-02', '2026-09-16'),
            (501, 'КН-103', '2026-09-04', '2026-09-18'),
            (502, 'КН-102', '2026-09-05', '2026-09-19'),
            (502, 'КН-105', '2026-09-10', '2026-09-24'),
            (503, 'КН-104', '2026-09-12', '2026-09-26'),
            (503, 'КН-106', '2026-09-15', '2026-09-29'),
            (504, 'КН-107', '2026-09-18', '2026-10-02'),
            (505, 'КН-108', '2026-09-20', '2026-10-04'),
            (506, 'КН-101', '2026-09-25', '2026-10-09'),
            (504, 'КН-102', '2026-09-28', '2026-10-12'),
        ]
        cur.executemany("INSERT INTO loans (reader_id, shifr, issue_date, return_date) VALUES (?, ?, ?, ?)", loans_data)

    conn.commit()
    conn.close()

def get_readers_dict():
    conn = get_connection()
    rows = conn.execute("SELECT reader_id, full_name, phone FROM readers ORDER BY reader_id").fetchall()
    conn.close()
    return {row["reader_id"]: f"№{row['reader_id']} — {row['full_name']} ({row['phone']})" for row in rows}

def get_books_dict():
    conn = get_connection()
    rows = conn.execute("SELECT shifr, title, author FROM books ORDER BY shifr").fetchall()
    conn.close()
    return {row["shifr"]: f"{row['shifr']} — «{row['title']}» ({row['author']})" for row in rows}

if __name__ == "__main__":
    init_db()
    print("Database library16.db initialized successfully at:", DB_PATH)
