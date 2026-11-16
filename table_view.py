import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection

# Цветовая гамма темы
BG_COLOR = "#F1F5F9"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_COLOR = "#2563EB"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"
HIGHLIGHT_BG = "#DBEAFE"
HIGHLIGHT_FG = "#1E40AF"

class TableViewForm(tk.Toplevel):
    def __init__(self, parent, initial_table="books"):
        super().__init__(parent)
        self.title("Табличный вид — Сортировка, фильтрация и поиск")
        self.geometry("860x650")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.current_table = initial_table
        self.raw_rows = []
        self.filtered_rows = []

        self._init_table_configs()
        self._build_ui()
        self.load_table_data(self.current_table)

    def _init_table_configs(self):
        self.table_configs = {
            "books": {
                "title": "Таблица «Книги» (Табличный вид)",
                "columns": [
                    ("shifr", "Шифр книги", 100),
                    ("author", "Автор", 180),
                    ("title", "Название книги", 220),
                    ("publisher", "Издательство", 130),
                    ("year", "Год издания", 90),
                ],
                "filter_col": "author",
                "filter_label": "Автор:",
                "sort_fields": ["Шифр книги", "Автор", "Название книги", "Издательство", "Год издания"],
                "query": "SELECT shifr, author, title, publisher, year FROM books ORDER BY shifr"
            },
            "libraries": {
                "title": "Таблица «Библиотеки» (Табличный вид)",
                "columns": [
                    ("number", "Номер филиала", 120),
                    ("address", "Адрес филиала", 320),
                    ("phone", "Контактный телефон", 220),
                ],
                "filter_col": "address",
                "filter_label": "Адрес:",
                "sort_fields": ["Номер филиала", "Адрес филиала", "Контактный телефон"],
                "query": "SELECT number, address, phone FROM libraries ORDER BY number"
            },
            "copies": {
                "title": "Таблица «Экземпляры» (Табличный вид)",
                "columns": [
                    ("id", "ID", 60),
                    ("lib_number", "Номер библиотеки", 130),
                    ("book_shifr", "Шифр книги", 110),
                    ("title", "Название книги", 210),
                    ("hall", "Читальный зал", 210),
                ],
                "filter_col": "hall",
                "filter_label": "Читальный зал:",
                "sort_fields": ["ID", "Номер библиотеки", "Шифр книги", "Название книги", "Читальный зал"],
                "query": """
                SELECT c.id, c.lib_number, c.book_shifr, b.title, c.hall
                FROM copies c
                JOIN books b ON c.book_shifr = b.shifr
                ORDER BY c.id
                """
            }
        }

    def _build_ui(self):
        # Переключатель таблиц вверху
        nav_top = tk.Frame(self, bg=BG_COLOR, padx=16, pady=8)
        nav_top.pack(fill=tk.X)

        tk.Label(nav_top, text="Выберите таблицу:", font=("Segoe UI", 9, "bold"),
                 bg=BG_COLOR, fg=PRIMARY_COLOR).pack(side=tk.LEFT, padx=(0, 8))

        self.tbl_var = tk.StringVar(value=self.current_table)
        for tbl_key, tbl_label in [("books", "Книги"), ("libraries", "Библиотеки"), ("copies", "Экземпляры")]:
            rb = tk.Radiobutton(nav_top, text=tbl_label, value=tbl_key, variable=self.tbl_var,
                                font=("Segoe UI", 9), bg=BG_COLOR, activebackground=BG_COLOR,
                                command=self._on_table_switch)
            rb.pack(side=tk.LEFT, padx=6)

        # 1. Заголовок таблицы (Label1 - темно-синий крупный заголовок)
        self.lbl_title = tk.Label(self, text="Таблица (Табличный вид)", font=("Segoe UI", 13, "bold"),
                                  fg=PRIMARY_COLOR, bg=BG_COLOR)
        self.lbl_title.pack(anchor="w", padx=16, pady=(4, 6))

        # Основной центральный контейнер: Слева таблица (DataGridView), справа панель управления
        main_box = tk.Frame(self, bg=BG_COLOR)
        main_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        # Левая часть: DataGridView
        grid_frame = tk.Frame(main_box, bg=CARD_BG, relief=tk.SOLID, bd=1)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.tree = ttk.Treeview(grid_frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(grid_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(grid_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        grid_frame.rowconfigure(0, weight=1)
        grid_frame.columnconfigure(0, weight=1)

        # Настройка стиля подписи строк и ячеек поиска
        self.tree.tag_configure("highlight", background=HIGHLIGHT_BG, foreground=HIGHLIGHT_FG)
        self.tree.tag_configure("normal", background="#FFFFFF", foreground=TEXT_COLOR)

        # Правая часть: Блок Сортировки (GroupBox1)
        right_box = tk.Frame(main_box, bg=BG_COLOR, width=280)
        right_box.pack(side=tk.RIGHT, fill=tk.Y)

        sort_group = tk.LabelFrame(right_box, text="Сортировка", font=("Segoe UI", 9, "bold"),
                                   bg=CARD_BG, fg=PRIMARY_COLOR, padx=10, pady=8, relief=tk.SOLID, bd=1)
        sort_group.pack(fill=tk.X, pady=(0, 10))

        tk.Label(sort_group, text="Поле для сортировки:", font=("Segoe UI", 9),
                 bg=CARD_BG, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 4))

        # Список полей (ListBox1)
        list_frame = tk.Frame(sort_group, bg=CARD_BG)
        list_frame.pack(fill=tk.X, pady=(0, 6))

        self.listbox = tk.Listbox(list_frame, height=5, font=("Segoe UI", 9),
                                  selectmode=tk.SINGLE, relief=tk.SOLID, bd=1)
        lb_vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_vsb.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # Переключатели направления сортировки
        self.sort_dir_var = tk.StringVar(value="ASC")
        rb_asc = tk.Radiobutton(sort_group, text="Сортировка по возрастанию", value="ASC",
                                variable=self.sort_dir_var, font=("Segoe UI", 8),
                                bg=CARD_BG, activebackground=CARD_BG)
        rb_asc.pack(anchor="w", pady=1)

        rb_desc = tk.Radiobutton(sort_group, text="Сортировка по убыванию", value="DESC",
                                 variable=self.sort_dir_var, font=("Segoe UI", 8),
                                 bg=CARD_BG, activebackground=CARD_BG)
        rb_desc.pack(anchor="w", pady=1)

        # Кнопка Сортировать (Button1 - разблокируется при выборе поля)
        self.btn_sort = tk.Button(sort_group, text="Сортировать", font=("Segoe UI", 9, "bold"),
                                  bg="#F1F5F9", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1,
                                  cursor="hand2", state="disabled", command=self.apply_sort)
        self.btn_sort.pack(fill=tk.X, pady=(8, 2))

        # Нижняя панель: Фильтрация, Поиск, Кнопки управления (Точно как на Рис. 11.10)
        bottom_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=10)
        bottom_card.pack(fill=tk.X, padx=16, pady=(6, 12))

        # Ряд 1: Фильтрация
        row_filter = tk.Frame(bottom_card, bg=CARD_BG)
        row_filter.pack(fill=tk.X, pady=3)

        self.lbl_filter = tk.Label(row_filter, text="Поле фильтра:", width=12, anchor="w",
                                   font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
        self.lbl_filter.pack(side=tk.LEFT)

        self.filter_var = tk.StringVar()
        self.cb_filter = ttk.Combobox(row_filter, textvariable=self.filter_var, font=("Segoe UI", 9),
                                      state="readonly", width=36)
        self.cb_filter.pack(side=tk.LEFT, padx=(0, 10))

        btn_filter = tk.Button(row_filter, text="Фильтровать", font=("Segoe UI", 9),
                               bg="#ECFDF5", fg="#047857", relief=tk.GROOVE, bd=1,
                               cursor="hand2", padx=10, command=self.apply_filter)
        btn_filter.pack(side=tk.LEFT, padx=4)

        btn_show_all = tk.Button(row_filter, text="Показать все", font=("Segoe UI", 9),
                                 bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1,
                                 cursor="hand2", padx=10, command=self.show_all_records)
        btn_show_all.pack(side=tk.LEFT, padx=4)

        # Ряд 2: Поиск
        row_search = tk.Frame(bottom_card, bg=CARD_BG)
        row_search.pack(fill=tk.X, pady=3)

        lbl_crit = tk.Label(row_search, text="Критерий:", width=12, anchor="w",
                            font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
        lbl_crit.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(row_search, textvariable=self.search_var, font=("Segoe UI", 9), width=38)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.apply_search())

        btn_search = tk.Button(row_search, text="Найти", font=("Segoe UI", 9, "bold"),
                               bg="#EFF6FF", fg=ACCENT_COLOR, relief=tk.GROOVE, bd=1,
                               cursor="hand2", padx=14, command=self.apply_search)
        btn_search.pack(side=tk.LEFT, padx=4)

        btn_close = tk.Button(row_search, text="Закрыть", font=("Segoe UI", 9),
                              bg="#FEF2F2", fg="#DC2626", relief=tk.GROOVE, bd=1,
                              cursor="hand2", padx=14, command=self.destroy)
        btn_close.pack(side=tk.RIGHT, padx=4)

        # Статусная строка
        self.status_var = tk.StringVar(value="Готово")
        lbl_status = tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 8),
                              bg=BG_COLOR, fg="#64748B", anchor="w", padx=18)
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 4))

    def _on_table_switch(self):
        new_tbl = self.tbl_var.get()
        if new_tbl != self.current_table:
            self.current_table = new_tbl
            self.load_table_data(new_tbl)

    def load_table_data(self, tbl_key):
        cfg = self.table_configs[tbl_key]
        self.lbl_title.config(text=cfg["title"])
        self.lbl_filter.config(text=cfg["filter_label"])

        # Очистка и настройка колонок Treeview
        for col in self.tree.get_children():
            self.tree.delete(col)

        col_ids = [c[0] for c in cfg["columns"]]
        self.tree["columns"] = col_ids
        for cid, cname, width in cfg["columns"]:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor="w")

        # Заполнение ListBox полями сортировки
        self.listbox.delete(0, tk.END)
        for sfield in cfg["sort_fields"]:
            self.listbox.insert(tk.END, sfield)
        self.btn_sort.config(state="disabled")

        # Загрузка данных из БД
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(cfg["query"])
        self.raw_rows = [list(row) for row in cur.fetchall()]
        conn.close()

        self.filtered_rows = list(self.raw_rows)
        self._populate_tree(self.filtered_rows)

        # Обновление выпадающего списка фильтра
        filter_idx = [c[0] for c in cfg["columns"]].index(cfg["filter_col"])
        unique_vals = sorted(list(set(str(r[filter_idx]) for r in self.raw_rows if r[filter_idx])))
        self.cb_filter["values"] = unique_vals
        if unique_vals:
            self.cb_filter.current(0)

        self.status_var.set(f"Загружено записей: {len(self.raw_rows)}")

    def _populate_tree(self, rows_list, highlight_indices=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        highlight_indices = highlight_indices or set()
        for idx, row in enumerate(rows_list):
            str_vals = [str(v) if v is not None else "" for v in row]
            tag = "highlight" if idx in highlight_indices else "normal"
            self.tree.insert("", "end", iid=str(idx), values=str_vals, tags=(tag,))

    def _on_listbox_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.btn_sort.config(state="normal", bg="#EFF6FF", fg=ACCENT_COLOR)

    def apply_sort(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        col_idx = sel[0]
        descending = (self.sort_dir_var.get() == "DESC")

        # Сортировка с учетом числовых типов
        def sort_key(item):
            val = item[col_idx]
            if isinstance(val, (int, float)):
                return val
            try:
                return int(val)
            except (ValueError, TypeError):
                return str(val).lower()

        self.filtered_rows.sort(key=sort_key, reverse=descending)
        self._populate_tree(self.filtered_rows)
        field_name = self.table_configs[self.current_table]["sort_fields"][col_idx]
        dir_text = "убыванию" if descending else "возрастанию"
        self.status_var.set(f"Отсортировано по полю '{field_name}' ({dir_text})")

    def apply_filter(self):
        val = self.filter_var.get().strip()
        if not val:
            return
        cfg = self.table_configs[self.current_table]
        filter_col_idx = [c[0] for c in cfg["columns"]].index(cfg["filter_col"])

        self.filtered_rows = [r for r in self.raw_rows if str(r[filter_col_idx]) == val]
        self._populate_tree(self.filtered_rows)
        self.status_var.set(f"Применен фильтр: {cfg['filter_label']} '{val}' (найдено: {len(self.filtered_rows)})")

    def show_all_records(self):
        self.filtered_rows = list(self.raw_rows)
        self._populate_tree(self.filtered_rows)
        self.search_var.set("")
        self.status_var.set(f"Отображены все записи (всего: {len(self.raw_rows)})")

    def apply_search(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self._populate_tree(self.filtered_rows)
            return

        matching_indices = set()
        for idx, row in enumerate(self.filtered_rows):
            for cell in row:
                if query in str(cell).lower():
                    matching_indices.add(idx)
                    break

        self._populate_tree(self.filtered_rows, highlight_indices=matching_indices)
        total_found = len(matching_indices)
        if total_found > 0:
            first_match = sorted(list(matching_indices))[0]
            self.tree.see(str(first_match))
            self.tree.selection_set(str(first_match))
            self.status_var.set(f"Поиск по критерию '{query}': найдено совпадений {total_found}")
        else:
            self.status_var.set(f"По запросу '{query}' ничего не найдено")
            messagebox.showinfo("Поиск", f"По критерию '{query}' записей не найдено.", parent=self)
