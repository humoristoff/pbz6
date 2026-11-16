import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from database import init_db, get_connection
from forms import BooksForm16, ReadersForm16, LoansForm16
from table_view import TableViewForm16
from reports import ReportViewerForm16

BG_MAIN = "#F8FAFC"
HEADER_BG = "#1E3A8A"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_COLOR = "#2563EB"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#E2E8F0"

class ModernMainWindow16(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИС «Библиотека» — Лабораторная работа № 6 (Вариант 16)")
        self.geometry("820x600")
        self.configure(bg=BG_MAIN)
        self.minsize(780, 560)

        init_db()
        self._build_menu()
        self._build_header()
        self._build_stats_panel()
        self._build_main_cards()
        self._build_footer()

    def _build_menu(self):
        menubar = tk.Menu(self)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Обновить данные", command=self.refresh_stats)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню Формы
        forms_menu = tk.Menu(menubar, tearoff=0)
        forms_menu.add_command(label="Книги (Каталог)", command=self.open_books)
        forms_menu.add_command(label="Читатели (Картотека)", command=self.open_readers)
        forms_menu.add_command(label="Выдача книг (Абонемент)", command=self.open_loans)
        menubar.add_cascade(label="Формы ввода", menu=forms_menu)

        # Меню Таблицы
        tables_menu = tk.Menu(menubar, tearoff=0)
        tables_menu.add_command(label="Табличный вид (Сортировка/Фильтр/Поиск)", command=self.open_table_view)
        menubar.add_cascade(label="Таблицы", menu=tables_menu)

        # Меню Отчеты
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="1. Каталог книжного фонда", command=lambda: self.open_reports(1))
        reports_menu.add_command(label="2. Картотека читателей", command=lambda: self.open_reports(2))
        reports_menu.add_command(label="3. Журнал учета выдачи книг", command=lambda: self.open_reports(3))
        reports_menu.add_command(label="4. Ведомость сроков возврата", command=lambda: self.open_reports(4))
        menubar.add_cascade(label="Отчеты", menu=reports_menu)

        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _build_header(self):
        hdr_frame = tk.Frame(self, bg=HEADER_BG, padx=24, pady=18)
        hdr_frame.pack(fill=tk.X)

        lbl_title = tk.Label(hdr_frame, text="ИНФОРМАЦИОННАЯ СИСТЕМА «БИБЛИОТЕКА»",
                             font=("Segoe UI", 16, "bold"), fg="#FFFFFF", bg=HEADER_BG)
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(hdr_frame,
                            text="Лабораторная работа № 6 • Организация табличного интерфейса и построение отчетов (Вариант 16)",
                            font=("Segoe UI", 10), fg="#93C5FD", bg=HEADER_BG)
        lbl_sub.pack(anchor="w", pady=(3, 0))

    def _build_stats_panel(self):
        stats_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=12)
        stats_frame.pack(fill=tk.X)

        self.stat_books = tk.StringVar(value="0")
        self.stat_readers = tk.StringVar(value="0")
        self.stat_loans = tk.StringVar(value="0")

        cards_data = [
            ("Книжный фонд", self.stat_books, "наименований в базе"),
            ("Читатели на учете", self.stat_readers, "активных абонентов"),
            ("Книг на руках", self.stat_loans, "текущих выдач"),
        ]

        for idx, (title, var, desc) in enumerate(cards_data):
            stats_frame.columnconfigure(idx, weight=1)
            card = tk.Frame(stats_frame, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=10)
            card.grid(row=0, column=idx, padx=6, sticky="ew")

            tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#64748B").pack(anchor="w")
            tk.Label(card, textvariable=var, font=("Segoe UI", 18, "bold"), bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor="w")
            tk.Label(card, text=desc, font=("Segoe UI", 8), bg=CARD_BG, fg="#94A3B8").pack(anchor="w")

        self.refresh_stats()

    def _build_main_cards(self):
        container = tk.Frame(self, bg=BG_MAIN, padx=20, pady=8)
        container.pack(fill=tk.BOTH, expand=True)

        actions = [
            ("Каталог книг", "Просмотр, ввод и редактирование книжного фонда библиотеки", self.open_books, "#2563EB"),
            ("Картотека читателей", "Учет абонентов, персональные данные, контакты и образование", self.open_readers, "#1E40AF"),
            ("Выдача литературы", "Регистрация выдачи книг читателям, фиксация сроков возврата", self.open_loans, "#1D4ED8"),
            ("Табличный интерфейс", "Сортировка по полям, фильтрация данных и быстрый контекстный поиск", self.open_table_view, "#0284C7"),
            ("Генератор отчетов", "Построение 4 аналитических отчетов, экспорт в HTML/TXT и печать", lambda: self.open_reports(1), "#0369A1"),
        ]

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        for idx, (btn_title, btn_desc, cmd, col) in enumerate(actions):
            r = idx // 2
            c = idx % 2
            colspan = 2 if idx == len(actions) - 1 and len(actions) % 2 != 0 else 1

            card = tk.Frame(container, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=10)
            card.grid(row=r, column=c, columnspan=colspan, padx=6, pady=6, sticky="nsew")
            container.rowconfigure(r, weight=1)

            btn = tk.Button(card, text=btn_title, font=("Segoe UI", 11, "bold"),
                            bg=col, fg="white", activebackground=PRIMARY_COLOR, activeforeground="white",
                            relief=tk.FLAT, cursor="hand2", padx=12, pady=6, command=cmd)
            btn.pack(anchor="w", fill=tk.X)

            tk.Label(card, text=btn_desc, font=("Segoe UI", 9), bg=CARD_BG, fg="#475569",
                     wraplength=320 if colspan == 1 else 680, justify="left").pack(anchor="w", pady=(6, 0))

    def _build_footer(self):
        footer = tk.Frame(self, bg="#EFF6FF", relief=tk.SOLID, bd=1, padx=20, pady=6)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(footer, text="БрГТУ • Факультет ЭИС • Кафедра ИИТ • Вариант 16 • Студент: Малич А.В. (ПО-9)",
                 font=("Segoe UI", 8), bg="#EFF6FF", fg="#475569").pack(side=tk.LEFT)
        tk.Label(footer, text="СУБД: SQLite3 + Python Tkinter UI",
                 font=("Segoe UI", 8, "bold"), bg="#EFF6FF", fg=PRIMARY_COLOR).pack(side=tk.RIGHT)

    def refresh_stats(self):
        try:
            conn = get_connection()
            b_cnt = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            r_cnt = conn.execute("SELECT COUNT(*) FROM readers").fetchone()[0]
            l_cnt = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
            conn.close()

            self.stat_books.set(str(b_cnt))
            self.stat_readers.set(str(r_cnt))
            self.stat_loans.set(str(l_cnt))
        except Exception:
            pass

    def open_books(self):
        BooksForm16(self, on_update_callback=self.refresh_stats)

    def open_readers(self):
        ReadersForm16(self, on_update_callback=self.refresh_stats)

    def open_loans(self):
        LoansForm16(self, on_update_callback=self.refresh_stats)

    def open_table_view(self):
        TableViewForm16(self)

    def open_reports(self, report_idx=1):
        ReportViewerForm16(self, default_report_index=report_idx)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа № 6 по дисциплине ПБЗ\n"
            "Тема: Организация пользовательского интерфейса: табличное представление и отчеты\n\n"
            "Студент: Малич А.В. (группа ПО-9, Вариант 16)\n"
            "Преподаватель: Савонюк В.А.\n"
            "Брестский государственный технический университет (БрГТУ), 2026 г."
        )

if __name__ == "__main__":
    app = ModernMainWindow16()
    app.mainloop()
