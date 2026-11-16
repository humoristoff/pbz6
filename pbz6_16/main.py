import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import init_db, get_connection
from forms import BooksForm16, ReadersForm16, LoansForm16
from table_view import TableViewForm16
from reports import ReportViewerForm16

BG_MAIN = "#F1F5F9"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E40AF" # Deep Navy Blue
ACCENT_BLUE = "#2563EB"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER_CLR = "#E2E8F0"

class ModernMainWindow16(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ИС \"Библиотека\" — Лабораторная работа № 6 (Вар. 16)")
        self.geometry("540x590")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.center_window(540, 590)
        init_db()

        self._build_menu()
        self._build_ui()
        self.update_stats()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Табличный вид (Поиск/Сортировка)", command=self.open_table_view)
        file_menu.add_command(label="Генератор отчетов", command=self.open_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        tables_menu = tk.Menu(menubar, tearoff=0)
        tables_menu.add_command(label="Книги", command=self.open_books)
        tables_menu.add_command(label="Читатели", command=self.open_readers)
        tables_menu.add_command(label="Выдача", command=self.open_loans)
        menubar.add_cascade(label="Таблицы", menu=tables_menu)

        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="1. Каталог фонда", command=lambda: self.open_reports(1))
        reports_menu.add_command(label="2. Картотека читателей", command=lambda: self.open_reports(2))
        reports_menu.add_command(label="3. Журнал учета выдачи", command=lambda: self.open_reports(3))
        reports_menu.add_command(label="4. Ведомость сроков возврата", command=lambda: self.open_reports(4))
        menubar.add_cascade(label="Отчеты", menu=reports_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        # 1. Заголовочная карточка (Header Banner)
        header_frame = tk.Frame(self, bg=PRIMARY_COLOR, padx=20, pady=16)
        header_frame.pack(fill=tk.X)

        lbl_app_name = tk.Label(header_frame, text="ИС «БИБЛИОТЕКА»", font=("Segoe UI", 15, "bold"),
                                fg="white", bg=PRIMARY_COLOR)
        lbl_app_name.pack(anchor="w")

        lbl_sub = tk.Label(header_frame, text="Лабораторная работа № 6 • Вариант 16 • Таблицы и отчеты",
                           font=("Segoe UI", 9), fg="#93C5FD", bg=PRIMARY_COLOR)
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # 2. Информационная плашка со статистикой БД
        stats_frame = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        stats_frame.pack(fill=tk.X, padx=16, pady=(10, 6))

        self.lbl_stats = tk.Label(stats_frame, text="Загрузка статистики...", font=("Segoe UI", 9),
                                  fg=TEXT_MUTED, bg=CARD_BG, pady=6)
        self.lbl_stats.pack()

        # 3. Карточный блок кнопок навигации (как в Лаб 5)
        buttons_frame = tk.Frame(self, bg=BG_MAIN)
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self._create_nav_button(buttons_frame, "Таблица «Книги»", "Каталог библиотечного фонда, авторы и издания", self.open_books)
        self._create_nav_button(buttons_frame, "Таблица «Читатели»", "Реестр читателей, контакты, адреса и образование", self.open_readers)
        self._create_nav_button(buttons_frame, "Таблица «Выдача»", "Журнал выданных книг и контроль дат возврата", self.open_loans)

        # 4. Табличный вид и отчеты (полноразмерные без обрезки)
        btn_grid = tk.Button(buttons_frame, text="Табличный вид (сортировка, фильтр, поиск)",
                             command=self.open_table_view,
                             font=("Segoe UI", 9, "bold"),
                             bg="#2563EB", fg="white", activebackground="#1D4ED8", activeforeground="white",
                             relief=tk.FLAT, cursor="hand2", pady=7)
        btn_grid.pack(fill=tk.X, pady=(6, 3))

        btn_rep = tk.Button(buttons_frame, text="Генератор аналитических отчетов",
                            command=self.open_reports,
                            font=("Segoe UI", 9, "bold"),
                            bg="#0284C7", fg="white", activebackground="#0369A1", activeforeground="white",
                            relief=tk.FLAT, cursor="hand2", pady=7)
        btn_rep.pack(fill=tk.X, pady=3)

        # 5. Кнопка выхода
        btn_exit = tk.Button(buttons_frame, text="Выход из системы", command=self.destroy,
                             font=("Segoe UI", 9), bg="#E2E8F0", fg=TEXT_DARK,
                             activebackground="#CBD5E1", relief=tk.FLAT, cursor="hand2", pady=5)
        btn_exit.pack(fill=tk.X, pady=(5, 4))

    def _create_nav_button(self, parent, title, subtitle, command):
        card = tk.Frame(parent, bg=CARD_BG, relief=tk.SOLID, bd=1, cursor="hand2")
        card.pack(fill=tk.X, pady=3)

        inner = tk.Frame(card, bg=CARD_BG, padx=12, pady=6)
        inner.pack(fill=tk.X)

        t_lbl = tk.Label(inner, text=title, font=("Segoe UI", 10, "bold"), fg=PRIMARY_COLOR, bg=CARD_BG, cursor="hand2")
        t_lbl.pack(anchor="w")

        s_lbl = tk.Label(inner, text=subtitle, font=("Segoe UI", 8), fg=TEXT_MUTED, bg=CARD_BG, cursor="hand2")
        s_lbl.pack(anchor="w")

        for w in (card, inner, t_lbl, s_lbl):
            w.bind("<Button-1>", lambda e, c=command: c())
            w.bind("<Enter>", lambda e, cd=card, i=inner, t=t_lbl, s=s_lbl: [
                cd.config(bg="#EFF6FF"), i.config(bg="#EFF6FF"), t.config(bg="#EFF6FF"), s.config(bg="#EFF6FF")
            ])
            w.bind("<Leave>", lambda e, cd=card, i=inner, t=t_lbl, s=s_lbl: [
                cd.config(bg=CARD_BG), i.config(bg=CARD_BG), t.config(bg=CARD_BG), s.config(bg=CARD_BG)
            ])

    def update_stats(self):
        try:
            conn = get_connection()
            b_cnt = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            r_cnt = conn.execute("SELECT COUNT(*) FROM readers").fetchone()[0]
            l_cnt = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
            conn.close()
            self.lbl_stats.config(text=f"В базе: {b_cnt} книг  |  {r_cnt} читателей  |  {l_cnt} оформленных выдач")
        except Exception:
            pass

    def open_books(self):
        BooksForm16(self, on_update_callback=self.update_stats)

    def open_readers(self):
        ReadersForm16(self, on_update_callback=self.update_stats)

    def open_loans(self):
        LoansForm16(self, on_update_callback=self.update_stats)

    def open_table_view(self):
        TableViewForm16(self)

    def open_reports(self, report_idx=1):
        ReportViewerForm16(self, default_report_index=report_idx)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа № 6 по дисциплине ПБЗ\n"
            "Тема: Организация пользовательского интерфейса: табличное представление и отчеты\n\n"
            "Студент: Малич А.В. (группа ИИ-28, Вариант 16)\n"
            "Преподаватель: Савонюк В.А.\n"
            "Брестский государственный технический университет (БрГТУ), 2026 г."
        )

if __name__ == "__main__":
    app = ModernMainWindow16()
    app.mainloop()
