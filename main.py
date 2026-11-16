import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

from database import init_db
from forms import BooksForm, LibrariesForm, CopiesForm
from table_view import TableViewForm
from reports import ReportViewerForm

WIN_BG = "#ECE9D8"
HEADER_COLOR = "#000080"
BTN_BG = "#F0EFEA"

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("База данных \"Библиотека\" (ЛР 6)")
        self.geometry("460x440")
        self.configure(bg=WIN_BG)
        self.resizable(False, False)

        self.center_window(460, 440)
        init_db()

        self._build_menu()
        self._build_ui()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_menu(self):
        menubar = tk.Menu(self)

        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Табличный вид", command=self.open_table_view)
        file_menu.add_command(label="Генератор отчетов", command=self.open_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.destroy)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Меню Формы
        forms_menu = tk.Menu(menubar, tearoff=0)
        forms_menu.add_command(label="Таблица \"Библиотеки\"", command=self.open_libraries)
        forms_menu.add_command(label="Таблица \"Книги\"", command=self.open_books)
        forms_menu.add_command(label="Таблица \"Экземпляры\"", command=self.open_copies)
        menubar.add_cascade(label="Формы", menu=forms_menu)

        # Меню Отчеты
        rep_menu = tk.Menu(menubar, tearoff=0)
        rep_menu.add_command(label="1. Каталог фонда", command=lambda: self.open_reports(1))
        rep_menu.add_command(label="2. Филиалы библиотек", command=lambda: self.open_reports(2))
        rep_menu.add_command(label="3. Распределение экземпляров", command=lambda: self.open_reports(3))
        rep_menu.add_command(label="4. Сводка по издательствам", command=lambda: self.open_reports(4))
        menubar.add_cascade(label="Отчеты", menu=rep_menu)

        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        self.config(menu=menubar)

    def _build_ui(self):
        outer_frame = tk.Frame(self, bg=WIN_BG, relief=tk.GROOVE, bd=2)
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        lbl_title = tk.Label(
            outer_frame,
            text="База данных \"Библиотека\"",
            font=("Microsoft Sans Serif", 14, "bold"),
            fg=HEADER_COLOR,
            bg=WIN_BG
        )
        lbl_title.pack(pady=(16, 4))

        lbl_sub = tk.Label(
            outer_frame,
            text="Лабораторная работа №6 (Вариант 17)",
            font=("Tahoma", 9),
            fg="#555555",
            bg=WIN_BG
        )
        lbl_sub.pack(pady=(0, 18))

        btn_style = {
            "font": ("Tahoma", 9),
            "width": 30,
            "height": 1,
            "bg": BTN_BG,
            "relief": tk.RAISED,
            "bd": 1,
            "cursor": "hand2"
        }

        btn_libs = tk.Button(outer_frame, text="Таблица \"Библиотеки\"", command=self.open_libraries, **btn_style)
        btn_libs.pack(pady=4)

        btn_books = tk.Button(outer_frame, text="Таблица \"Книги\"", command=self.open_books, **btn_style)
        btn_books.pack(pady=4)

        btn_copies = tk.Button(outer_frame, text="Таблица \"Экземпляры\"", command=self.open_copies, **btn_style)
        btn_copies.pack(pady=4)

        sep1 = ttk.Separator(outer_frame, orient=tk.HORIZONTAL)
        sep1.pack(fill=tk.X, padx=30, pady=10)

        # Кнопка открытия табличного вида с сортировкой и фильтрами
        btn_grid = tk.Button(
            outer_frame,
            text="Табличный вид (Сортировка/Фильтр/Поиск)",
            command=self.open_table_view,
            font=("Tahoma", 9, "bold"),
            width=34,
            bg="#E2EBF5",
            relief=tk.RAISED,
            bd=1,
            cursor="hand2"
        )
        btn_grid.pack(pady=4)

        # Кнопка открытия построителя отчетов
        btn_rep = tk.Button(
            outer_frame,
            text="Генератор аналитических отчетов",
            command=self.open_reports,
            font=("Tahoma", 9, "bold"),
            width=34,
            bg="#E2F5E8",
            relief=tk.RAISED,
            bd=1,
            cursor="hand2"
        )
        btn_rep.pack(pady=4)

        # Кнопка Выход
        btn_exit = tk.Button(
            outer_frame,
            text="Выход",
            command=self.destroy,
            font=("Tahoma", 9),
            width=15,
            bg=BTN_BG,
            relief=tk.RAISED,
            bd=1
        )
        btn_exit.pack(pady=(12, 8))

    def open_books(self):
        BooksForm(self)

    def open_libraries(self):
        LibrariesForm(self)

    def open_copies(self):
        CopiesForm(self)

    def open_table_view(self):
        TableViewForm(self)

    def open_reports(self, report_idx=1):
        ReportViewerForm(self, default_report_index=report_idx)

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Лабораторная работа № 6 по дисциплине ПБЗ\n"
            "Тема: Создание приложения для работы с БД: табличное представление и отчеты\n\n"
            "Студент: Манцевич Р.С. (группа ИИ-28, Вариант 17)\n"
            "Преподаватель: Савонюк В.А.\n"
            "Брестский государственный технический университет (БрГТУ), 2026 г."
        )

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
