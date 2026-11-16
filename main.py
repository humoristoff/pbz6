import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import init_db, get_connection, get_db_stats
from forms import BooksForm, LibrariesForm, CopiesForm
from table_view import TableViewForm
from reports import ReportViewerForm

BG_MAIN = "#F1F5F9"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_BLUE = "#2563EB"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#64748B"
BORDER_CLR = "#CBD5E1"

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("АСУ «Библиотека» — Лабораторная работа № 6 (Вариант 17)")
        self.geometry("540x580")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.center_window(540, 580)
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
        file_menu.add_command(label="Табличный вид (сортировка, фильтрация)", command=self.open_table_view)
        file_menu.add_command(label="Генератор отчетов...", command=self.open_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        tables_menu = tk.Menu(menubar, tearoff=0)
        tables_menu.add_command(label="Книги", command=self.open_books)
        tables_menu.add_command(label="Библиотеки", command=self.open_libraries)
        tables_menu.add_command(label="Экземпляры", command=self.open_copies)
        menubar.add_cascade(label="Таблицы", menu=tables_menu)

        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Отчет 1: Каталог книжного фонда", command=lambda: ReportViewerForm(self, 1))
        reports_menu.add_command(label="Отчет 2: Справочник библиотечных отделений", command=lambda: ReportViewerForm(self, 2))
        reports_menu.add_command(label="Отчет 3: Ведомость распределения экземпляров", command=lambda: ReportViewerForm(self, 3))
        reports_menu.add_command(label="Отчет 4: Сводный по издательствам", command=lambda: ReportViewerForm(self, 4))
        menubar.add_cascade(label="Отчеты", menu=reports_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        # 1. Заголовочная карточка
        header_frame = tk.Frame(self, bg=PRIMARY_COLOR, padx=20, pady=16)
        header_frame.pack(fill=tk.X)

        lbl_app_name = tk.Label(header_frame, text="АСУ «БИБЛИОТЕКА»", font=("Segoe UI", 15, "bold"),
                                fg="white", bg=PRIMARY_COLOR)
        lbl_app_name.pack(anchor="w")

        lbl_sub = tk.Label(header_frame, text="Лабораторная работа № 6 • Вариант 17 • Таблицы и отчеты",
                           font=("Segoe UI", 9), fg="#93C5FD", bg=PRIMARY_COLOR)
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # 2. Информационная плашка со статистикой БД
        stats_frame = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        stats_frame.pack(fill=tk.X, padx=16, pady=(12, 6))

        stats_hdr = tk.Label(stats_frame, text="Текущее состояние базы данных:",
                             font=("Segoe UI", 9, "bold"), fg=PRIMARY_COLOR, bg=CARD_BG)
        stats_hdr.pack(anchor="w", padx=12, pady=(8, 4))

        self.lbl_stats = tk.Label(stats_frame, text="Загрузка статистики...", font=("Segoe UI", 9),
                                  fg=TEXT_DARK, bg=CARD_BG)
        self.lbl_stats.pack(anchor="w", padx=12, pady=(0, 8))

        # 3. Карточки действий для открытия форм и отчетов
        actions_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        actions_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)

        actions_title = tk.Label(actions_card, text="Разделы системы, табличный интерфейс и отчеты:",
                                 font=("Segoe UI", 10, "bold"), fg=TEXT_DARK, bg=CARD_BG)
        actions_title.pack(anchor="w", padx=14, pady=(10, 6))

        btns_container = tk.Frame(actions_card, bg=CARD_BG)
        btns_container.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        btn_specs = [
            ("Книги фонда", "Каталог литературы с навигатором, кнопками 'Таблица' и 'Отчёт'", self.open_books, "#1E40AF"),
            ("Филиалы библиотек", "Сеть библиотечных филиалов и контактные данные", self.open_libraries, "#0D9488"),
            ("Экземпляры книг", "Учет распределения фонда по читальным залам", self.open_copies, "#047857"),
            ("Табличный вид (Сортировка, фильтрация, поиск)", "Табличная форма с блоком сортировки по столбцам и фильтра", self.open_table_view, "#0369A1"),
            ("Генератор отчетов (4 аналитических отчета)", "Построение и печать 4 сводных отчетов по каталогу и филиалам", self.open_reports, "#7C3AED"),
        ]

        for text_main, text_desc, cmd, border_color in btn_specs:
            btn_box = tk.Frame(btns_container, bg="#F8FAFC", relief=tk.SOLID, bd=1, cursor="hand2")
            btn_box.pack(fill=tk.X, pady=3)
            btn_box.bind("<Button-1>", lambda e, c=cmd: c())

            lbl_m = tk.Label(btn_box, text=text_main, font=("Segoe UI", 9, "bold"), fg=border_color, bg="#F8FAFC", cursor="hand2")
            lbl_m.pack(anchor="w", padx=10, pady=(4, 1))
            lbl_m.bind("<Button-1>", lambda e, c=cmd: c())

            lbl_d = tk.Label(btn_box, text=text_desc, font=("Segoe UI", 8), fg=TEXT_MUTED, bg="#F8FAFC", cursor="hand2")
            lbl_d.pack(anchor="w", padx=10, pady=(0, 4))
            lbl_d.bind("<Button-1>", lambda e, c=cmd: c())

        # 4. Нижний статус-бар
        bottom_frame = tk.Frame(self, bg=PRIMARY_COLOR, padx=12, pady=6)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_author = tk.Label(bottom_frame, text="Студент: Манцевич Р.С.  |  Группа: ИИ-28  |  БрГТУ",
                              font=("Segoe UI", 8), fg="white", bg=PRIMARY_COLOR)
        lbl_author.pack(side=tk.LEFT)

        lbl_ver = tk.Label(bottom_frame, text="Лабораторная работа №6", font=("Segoe UI", 8),
                           fg="#93C5FD", bg=PRIMARY_COLOR)
        lbl_ver.pack(side=tk.RIGHT)

    def update_stats(self):
        try:
            stats = get_db_stats()
            txt = (f"Книг: {stats['books']}  |  "
                   f"Филиалов: {stats['libraries']}  |  "
                   f"Экземпляров: {stats['copies']}")
            self.lbl_stats.config(text=txt)
        except Exception as e:
            self.lbl_stats.config(text=f"Ошибка чтения базы данных: {e}")

    def open_books(self):
        BooksForm(self, on_update_callback=self.update_stats)

    def open_libraries(self):
        LibrariesForm(self, on_update_callback=self.update_stats)

    def open_copies(self):
        CopiesForm(self, on_update_callback=self.update_stats)

    def open_table_view(self):
        TableViewForm(self)

    def open_reports(self):
        ReportViewerForm(self)

    def show_about(self):
        msg = ("АСУ «Библиотека»\n"
               "Лабораторная работа № 6\n"
               "Тема: Создание приложения для работы с БД: табличное представление и отчеты\n\n"
               "Выполнил:\n"
               "Студент 3 курса группы ИИ-28\n"
               "Манцевич Р.С. (Вариант 17)\n\n"
               "Преподаватель:\n"
               "Савонюк В. А.\n\n"
               "БрГТУ, Брест, 2026")
        messagebox.showinfo("О программе", msg, parent=self)

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
