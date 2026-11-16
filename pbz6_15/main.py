import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import init_db, get_connection
from forms import SkladyForm, ProizvoditeliForm, TovaryForm
from table_view import TableViewForm15
from reports import ReportViewerForm15

BG_MAIN = "#F0FDF4"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#0F766E" # Deep Teal
ACCENT_COLOR = "#047857"  # Deep Emerald
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER_CLR = "#CBD5E1"

class WarehouseMainWindow15(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("АСУ «Склад товаров» — Лабораторная работа № 6 (Вариант 15)")
        self.geometry("560x610")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.center_window(560, 610)
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
        tables_menu.add_command(label="Склады", command=self.open_sklady)
        tables_menu.add_command(label="Производители", command=self.open_proiz)
        tables_menu.add_command(label="Товары", command=self.open_tovary)
        menubar.add_cascade(label="Справочники", menu=tables_menu)

        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="1. Ведомость складских остатков", command=lambda: self.open_reports(1))
        reports_menu.add_command(label="2. Справочник складов и емкостей", command=lambda: self.open_reports(2))
        reports_menu.add_command(label="3. Реестр заводов-производителей", command=lambda: self.open_reports(3))
        reports_menu.add_command(label="4. Инвентаризационная ведомость", command=lambda: self.open_reports(4))
        menubar.add_cascade(label="Отчеты", menu=reports_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        # 1. Заголовочная карточка (Header Banner)
        header_frame = tk.Frame(self, bg=PRIMARY_COLOR, padx=20, pady=16)
        header_frame.pack(fill=tk.X)

        lbl_app_name = tk.Label(header_frame, text="АСУ «СКЛАД ТОВАРОВ»", font=("Segoe UI", 15, "bold"),
                                fg="white", bg=PRIMARY_COLOR)
        lbl_app_name.pack(anchor="w")

        lbl_sub = tk.Label(header_frame, text="Лабораторная работа № 6 • Вариант 15 • Складской учет и отчеты",
                           font=("Segoe UI", 9), fg="#99F6E4", bg=PRIMARY_COLOR)
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # 2. Информационная плашка со статистикой БД
        stats_frame = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        stats_frame.pack(fill=tk.X, padx=16, pady=(10, 6))

        stats_hdr = tk.Label(stats_frame, text="Текущее состояние базы данных:",
                             font=("Segoe UI", 9, "bold"), fg=PRIMARY_COLOR, bg=CARD_BG)
        stats_hdr.pack(anchor="w", padx=12, pady=(6, 2))

        self.lbl_stats = tk.Label(stats_frame, text="Загрузка статистики...", font=("Segoe UI", 9),
                                  fg=TEXT_DARK, bg=CARD_BG)
        self.lbl_stats.pack(anchor="w", padx=12, pady=(0, 6))

        # 3. Карточки действий для открытия таблиц и отчетов (полноразмерные карточки без обрезки)
        actions_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        actions_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)

        actions_title = tk.Label(actions_card, text="Разделы системы, экранные формы и отчеты:",
                                 font=("Segoe UI", 10, "bold"), fg=TEXT_DARK, bg=CARD_BG)
        actions_title.pack(anchor="w", padx=14, pady=(8, 4))

        btns_container = tk.Frame(actions_card, bg=CARD_BG)
        btns_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 8))

        btn_specs = [
            ("Склады предприятия", "Управление складами, адресами и организациями", self.open_sklady, "#0F766E"),
            ("Производители товаров", "Справочник заводов-изготовителей и стран происхождения", self.open_proiz, "#0D9488"),
            ("Товары на складах", "Поэкземплярный учет номенклатуры, остатков и единиц хранения", self.open_tovary, "#047857"),
            ("Табличный интерфейс", "Сортировка записей, гибкая фильтрация и контекстный поиск", self.open_table_view, "#0284C7"),
            ("Генератор отчетов и экспорт", "Построение 4 аналитических отчетов, экспорт в HTML/TXT и печать", self.open_reports, "#0369A1"),
        ]

        for text_main, text_desc, cmd, border_color in btn_specs:
            btn_box = tk.Frame(btns_container, bg="#F8FAFC", relief=tk.SOLID, bd=1, cursor="hand2")
            btn_box.pack(fill=tk.X, pady=3)
            btn_box.bind("<Button-1>", lambda e, c=cmd: c())

            lbl_m = tk.Label(btn_box, text=text_main, font=("Segoe UI", 10, "bold"), fg=border_color, bg="#F8FAFC", cursor="hand2")
            lbl_m.pack(anchor="w", padx=10, pady=(5, 1))
            lbl_m.bind("<Button-1>", lambda e, c=cmd: c())

            lbl_d = tk.Label(btn_box, text=text_desc, font=("Segoe UI", 8), fg=TEXT_MUTED, bg="#F8FAFC", cursor="hand2")
            lbl_d.pack(anchor="w", padx=10, pady=(0, 5))
            lbl_d.bind("<Button-1>", lambda e, c=cmd: c())

            for w in (btn_box, lbl_m, lbl_d):
                w.bind("<Enter>", lambda e, b=btn_box, m=lbl_m, d=lbl_d: [b.config(bg="#F0FDF4"), m.config(bg="#F0FDF4"), d.config(bg="#F0FDF4")])
                w.bind("<Leave>", lambda e, b=btn_box, m=lbl_m, d=lbl_d: [b.config(bg="#F8FAFC"), m.config(bg="#F8FAFC"), d.config(bg="#F8FAFC")])

        # 4. Кнопка выхода
        btn_exit = tk.Button(self, text="Выход из программы", command=self.destroy,
                             font=("Segoe UI", 9), bg="#E2E8F0", fg=TEXT_DARK,
                             activebackground="#CBD5E1", relief=tk.FLAT, cursor="hand2", pady=5)
        btn_exit.pack(fill=tk.X, padx=16, pady=(4, 10))

    def update_stats(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sklady")
            cnt_s = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM proizvoditeli")
            cnt_p = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*), SUM(Kol) FROM tovary")
            row_t = cur.fetchone()
            cnt_t = row_t[0]
            sum_kol = row_t[1] or 0
            conn.close()

            self.lbl_stats.config(
                text=f"Складов: {cnt_s}  |  Производителей: {cnt_p}  |  Товаров: {cnt_t} наим. ({sum_kol} ед.)"
            )
        except Exception:
            pass

    def open_sklady(self):
        SkladyForm(self, on_update_callback=self.update_stats)

    def open_proiz(self):
        ProizvoditeliForm(self, on_update_callback=self.update_stats)

    def open_tovary(self):
        TovaryForm(self, on_update_callback=self.update_stats)

    def open_table_view(self):
        TableViewForm15(self)

    def open_reports(self, report_idx=1):
        ReportViewerForm15(self, default_report_index=report_idx)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа № 6 по дисциплине ПБЗ\n"
            "Тема: Организация пользовательского интерфейса: табличное представление и отчеты\n\n"
            "Студентка: Маковей Е.В. (группа ИИ-28, Вариант 15)\n"
            "Преподаватель: Савонюк В.А.\n"
            "Брестский государственный технический университет (БрГТУ), 2026 г."
        )

if __name__ == "__main__":
    app = WarehouseMainWindow15()
    app.mainloop()
