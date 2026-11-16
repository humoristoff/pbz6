import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection

WIN_BG = "#ECE9D8"
HEADER_COLOR = "#000080"
BTN_BG = "#F0EFEA"
HIGHLIGHT_BG = "#B0D4F1"
HIGHLIGHT_FG = "#000000"

class TableViewForm(tk.Toplevel):
    def __init__(self, parent, initial_table="books"):
        super().__init__(parent)
        self.title("Табличный вид — Сортировка, фильтрация и поиск")
        self.geometry("860x640")
        self.configure(bg=WIN_BG)
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
        # Панель переключения таблиц вверху
        nav_top = tk.Frame(self, bg=WIN_BG, padx=14, pady=6)
        nav_top.pack(fill=tk.X)

        tk.Label(nav_top, text="Выберите таблицу:", font=("Tahoma", 9, "bold"),
                 bg=WIN_BG, fg=HEADER_COLOR).pack(side=tk.LEFT, padx=(0, 8))

        self.tbl_var = tk.StringVar(value=self.current_table)
        for tbl_key, tbl_label in [("books", "Книги"), ("libraries", "Библиотеки"), ("copies", "Экземпляры")]:
            rb = tk.Radiobutton(nav_top, text=tbl_label, value=tbl_key, variable=self.tbl_var,
                                font=("Tahoma", 9), bg=WIN_BG, activebackground=WIN_BG,
                                command=self._on_table_switch)
            rb.pack(side=tk.LEFT, padx=6)

        # Заголовок таблицы (синий крупный заголовок WinForms)
        self.lbl_title = tk.Label(self, text="Таблица (Табличный вид)", font=("Microsoft Sans Serif", 14, "bold"),
                                  fg=HEADER_COLOR, bg=WIN_BG)
        self.lbl_title.pack(anchor="w", padx=16, pady=(2, 6))

        # Основной контейнер: Слева DataGridView, справа GroupBox Сортировки
        main_box = tk.Frame(self, bg=WIN_BG)
        main_box.pack(fill=tk.BOTH, expand=True, padx=14, pady=2)

        # Левая часть: DataGridView
        grid_frame = tk.Frame(main_box, bg=WIN_BG, relief=tk.SUNKEN, bd=2)
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

        self.tree.tag_configure("highlight", background=HIGHLIGHT_BG, foreground=HIGHLIGHT_FG)
        self.tree.tag_configure("normal", background="#FFFFFF", foreground="#000000")

        # Правая часть: GroupBox Сортировка (по методичке WinForms)
        sort_group = tk.LabelFrame(main_box, text="Сортировка", font=("Tahoma", 9, "bold"),
                                   bg=WIN_BG, fg=HEADER_COLOR, padx=10, pady=8, relief=tk.GROOVE, bd=2)
        sort_group.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(sort_group, text="Поле для сортировки:", font=("Tahoma", 9),
                 bg=WIN_BG, fg="#000000", anchor="w").pack(fill=tk.X, pady=(0, 4))

        list_frame = tk.Frame(sort_group, bg=WIN_BG)
        list_frame.pack(fill=tk.X, pady=(0, 6))

        self.listbox = tk.Listbox(list_frame, height=5, font=("Tahoma", 9),
                                  selectmode=tk.SINGLE, relief=tk.SUNKEN, bd=1)
        lb_vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_vsb.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        self.sort_dir_var = tk.StringVar(value="ASC")
        rb_asc = tk.Radiobutton(sort_group, text="Сортировка по возрастанию", value="ASC",
                                variable=self.sort_dir_var, font=("Tahoma", 8),
                                bg=WIN_BG, activebackground=WIN_BG)
        rb_asc.pack(anchor="w", pady=1)

        rb_desc = tk.Radiobutton(sort_group, text="Сортировка по убыванию", value="DESC",
                                 variable=self.sort_dir_var, font=("Tahoma", 8),
                                 bg=WIN_BG, activebackground=WIN_BG)
        rb_desc.pack(anchor="w", pady=1)

        self.btn_sort = tk.Button(sort_group, text="Сортировать", font=("Tahoma", 9, "bold"),
                                  bg=BTN_BG, relief=tk.RAISED, bd=1,
                                  cursor="hand2", state="disabled", command=self.apply_sort)
        self.btn_sort.pack(fill=tk.X, pady=(8, 2))

        # Нижняя панель: Фильтрация, Поиск, Кнопки управления (Рис. 11.10)
        bottom_panel = tk.Frame(self, bg=WIN_BG, relief=tk.GROOVE, bd=2, padx=12, pady=8)
        bottom_panel.pack(fill=tk.X, padx=14, pady=(6, 8))

        # Ряд 1: Фильтрация
        row_filter = tk.Frame(bottom_panel, bg=WIN_BG)
        row_filter.pack(fill=tk.X, pady=3)

        self.lbl_filter = tk.Label(row_filter, text="Поле фильтра:", width=13, anchor="w",
                                   font=("Tahoma", 9, "bold"), bg=WIN_BG)
        self.lbl_filter.pack(side=tk.LEFT)

        self.filter_var = tk.StringVar()
        self.cb_filter = ttk.Combobox(row_filter, textvariable=self.filter_var, font=("Tahoma", 9),
                                      state="readonly", width=36)
        self.cb_filter.pack(side=tk.LEFT, padx=(0, 10))

        btn_filter = tk.Button(row_filter, text="Фильтровать", font=("Tahoma", 9),
                               bg=BTN_BG, relief=tk.RAISED, bd=1,
                               cursor="hand2", padx=10, command=self.apply_filter)
        btn_filter.pack(side=tk.LEFT, padx=4)

        btn_show_all = tk.Button(row_filter, text="Показать все", font=("Tahoma", 9),
                                 bg=BTN_BG, relief=tk.RAISED, bd=1,
                                 cursor="hand2", padx=10, command=self.show_all_records)
        btn_show_all.pack(side=tk.LEFT, padx=4)

        # Ряд 2: Поиск
        row_search = tk.Frame(bottom_panel, bg=WIN_BG)
        row_search.pack(fill=tk.X, pady=3)

        lbl_crit = tk.Label(row_search, text="Критерий:", width=13, anchor="w",
                            font=("Tahoma", 9, "bold"), bg=WIN_BG)
        lbl_crit.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(row_search, textvariable=self.search_var, font=("Tahoma", 9),
                                     width=38, relief=tk.SUNKEN, bd=1)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.apply_search())

        btn_search = tk.Button(row_search, text="Найти", font=("Tahoma", 9, "bold"),
                               bg=BTN_BG, relief=tk.RAISED, bd=1,
                               cursor="hand2", padx=14, command=self.apply_search)
        btn_search.pack(side=tk.LEFT, padx=4)

        btn_close = tk.Button(row_search, text="Закрыть", font=("Tahoma", 9),
                              bg=BTN_BG, relief=tk.RAISED, bd=1,
                              cursor="hand2", padx=14, command=self.destroy)
        btn_close.pack(side=tk.RIGHT, padx=4)

        # Статусная строка
        self.status_var = tk.StringVar(value="Готово")
        lbl_status = tk.Label(self, textvariable=self.status_var, font=("Tahoma", 8),
                              bg=WIN_BG, fg="#555555", anchor="w", padx=18)
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

        for col in self.tree.get_children():
            self.tree.delete(col)

        col_ids = [c[0] for c in cfg["columns"]]
        self.tree["columns"] = col_ids
        for cid, cname, width in cfg["columns"]:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor="w")

        self.listbox.delete(0, tk.END)
        for sfield in cfg["sort_fields"]:
            self.listbox.insert(tk.END, sfield)
        self.btn_sort.config(state="disabled")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(cfg["query"])
        rows = cur.fetchall()
        conn.close()

        self.raw_rows = [list(r) for r in rows]
        self.filtered_rows = list(self.raw_rows)

        self._populate_grid(self.filtered_rows)

        filter_col_idx = col_ids.index(cfg["filter_col"])
        vals = sorted(list(set(str(r[filter_col_idx]) for r in self.raw_rows if r[filter_col_idx] is not None)))
        self.cb_filter["values"] = vals
        if vals:
            self.cb_filter.current(0)
        else:
            self.filter_var.set("")

        self.status_var.set(f"Загружено записей: {len(self.filtered_rows)}")

    def _populate_grid(self, rows_to_display, highlight_set=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        highlight_set = highlight_set or set()
        for idx, row in enumerate(rows_to_display):
            tag = "highlight" if idx in highlight_set else "normal"
            self.tree.insert("", tk.END, values=row, tags=(tag,))

    def _on_listbox_select(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.btn_sort.config(state="normal")
        else:
            self.btn_sort.config(state="disabled")

    def apply_sort(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        col_idx = sel[0]
        direction = self.sort_dir_var.get()
        reverse = (direction == "DESC")

        def sort_key(row):
            val = row[col_idx]
            if val is None:
                return (1, "")
            try:
                return (0, float(val))
            except ValueError:
                return (0, str(val).lower())

        self.filtered_rows.sort(key=sort_key, reverse=reverse)
        self._populate_grid(self.filtered_rows)

        dir_ru = "по убыванию" if reverse else "по возрастанию"
        fname = self.table_configs[self.current_table]["sort_fields"][col_idx]
        self.status_var.set(f"Сортировка по полю '{fname}' ({dir_ru}). Строк: {len(self.filtered_rows)}")

    def apply_filter(self):
        val = self.filter_var.get().strip()
        if not val:
            messagebox.showwarning("Внимание", "Выберите значение для фильтрации!", parent=self)
            return

        cfg = self.table_configs[self.current_table]
        col_ids = [c[0] for c in cfg["columns"]]
        col_idx = col_ids.index(cfg["filter_col"])

        self.filtered_rows = [r for r in self.raw_rows if str(r[col_idx]) == val]
        self._populate_grid(self.filtered_rows)
        self.status_var.set(f"Фильтр: {cfg['filter_label']} '{val}'. Записей: {len(self.filtered_rows)}")

    def show_all_records(self):
        self.filtered_rows = list(self.raw_rows)
        self._populate_grid(self.filtered_rows)
        self.search_var.set("")
        self.status_var.set(f"Показаны все записи: {len(self.filtered_rows)}")

    def apply_search(self):
        crit = self.search_var.get().strip().lower()
        if not crit:
            messagebox.showwarning("Внимание", "Введите текст для поиска в поле 'Критерий'!", parent=self)
            return

        matches_indices = set()
        for idx, row in enumerate(self.filtered_rows):
            row_str = " ".join(str(cell).lower() for cell in row)
            if crit in row_str:
                matches_indices.add(idx)

        self._populate_grid(self.filtered_rows, highlight_set=matches_indices)

        if matches_indices:
            self.status_var.set(f"Поиск '{crit}': найдено {len(matches_indices)} совпадений")
            first_idx = sorted(list(matches_indices))[0]
            items = self.tree.get_children()
            if items:
                self.tree.see(items[first_idx])
                self.tree.selection_set(items[first_idx])
        else:
            self.status_var.set(f"Поиск '{crit}': совпадений не найдено")
            messagebox.showinfo("Результат поиска", f"Записей, содержащих '{crit}', не обнаружено.", parent=self)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    win = TableViewForm(root)
    win.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
