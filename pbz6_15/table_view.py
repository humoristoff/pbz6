import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection

BG_COLOR = "#F0FDF4"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#0F766E"
ACCENT_COLOR = "#047857"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"
HIGHLIGHT_BG = "#CCFBF1"
HIGHLIGHT_FG = "#0F766E"

class TableViewForm15(tk.Toplevel):
    def __init__(self, parent, initial_table="tovary"):
        super().__init__(parent)
        self.title("Табличный вид — Сортировка, фильтрация и поиск (Склад товаров)")
        self.geometry("980x660")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.current_table = initial_table
        self.raw_rows = []
        self.filtered_rows = []
        self.sort_direction = "ASC"

        self._init_table_configs()
        self._build_ui()
        self.load_table_data(self.current_table)

    def _init_table_configs(self):
        self.table_configs = {
            "tovary": {
                "title": "Таблица «Товары» (Табличный вид)",
                "columns": [
                    ("kod_tovara", "Код товара", 85),
                    ("name_t", "Наименование товара", 185),
                    ("firma", "Склад / Организация", 165),
                    ("name_proiz", "Производитель", 155),
                    ("edizmer", "Ед. изм.", 80),
                    ("kol", "Количество", 90),
                ],
                "filter_col": "name_t",
                "filter_label": "Товар:",
                "sort_fields": ["Код товара", "Наименование товара", "Склад / Организация", "Производитель", "Ед. изм.", "Количество"],
                "query": """
                SELECT t.kod_tovara, t.name_t, s.firma, p.name_proiz, t.edizmer, t.kol
                FROM tovary t
                JOIN sklady s ON t.kod_sklada = s.kod_sklada
                JOIN proizvoditeli p ON t.kod_proiz = p.kod_proiz
                ORDER BY t.kod_tovara
                """
            },
            "sklady": {
                "title": "Таблица «Склады» (Табличный вид)",
                "columns": [
                    ("kod_sklada", "Код склада", 90),
                    ("firma", "Организация / Склад", 220),
                    ("gorod", "Город", 160),
                    ("tip_hran", "Тип хранилища", 180),
                ],
                "filter_col": "gorod",
                "filter_label": "Город склада:",
                "sort_fields": ["Код склада", "Организация / Склад", "Город", "Тип хранилища"],
                "query": "SELECT kod_sklada, firma, gorod, tip_hran FROM sklady ORDER BY kod_sklada"
            },
            "proizvoditeli": {
                "title": "Таблица «Производители» (Табличный вид)",
                "columns": [
                    ("kod_proiz", "Код", 70),
                    ("name_proiz", "Производитель", 180),
                    ("adres_proiz", "Адрес завода", 200),
                    ("telefon_proiz", "Телефон", 130),
                    ("strana", "Страна", 120),
                ],
                "filter_col": "strana",
                "filter_label": "Страна:",
                "sort_fields": ["Код", "Производитель", "Адрес завода", "Телефон", "Страна"],
                "query": "SELECT kod_proiz, name_proiz, adres_proiz, telefon_proiz, strana FROM proizvoditeli ORDER BY kod_proiz"
            }
        }

    def _build_ui(self):
        nav_top = tk.Frame(self, bg=BG_COLOR, padx=16, pady=8)
        nav_top.pack(fill=tk.X)

        tk.Label(nav_top, text="Выберите таблицу:", font=("Segoe UI", 9, "bold"),
                 bg=BG_COLOR, fg=PRIMARY_COLOR).pack(side=tk.LEFT, padx=(0, 8))

        self.tbl_var = tk.StringVar(value=self.current_table)
        for tbl_key, tbl_label in [("tovary", "Товары"), ("sklady", "Склады"), ("proizvoditeli", "Производители")]:
            rb = tk.Radiobutton(nav_top, text=tbl_label, value=tbl_key, variable=self.tbl_var,
                                font=("Segoe UI", 9), bg=BG_COLOR, activebackground=BG_COLOR,
                                command=self._on_table_switch)
            rb.pack(side=tk.LEFT, padx=6)

        self.lbl_title = tk.Label(self, text="Таблица (Табличный вид)", font=("Segoe UI", 13, "bold"),
                                  fg=PRIMARY_COLOR, bg=BG_COLOR)
        self.lbl_title.pack(anchor="w", padx=16, pady=(4, 6))

        # Основной контейнер с надежной сеткой (grid)
        main_box = tk.Frame(self, bg=BG_COLOR)
        main_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)
        main_box.columnconfigure(0, weight=1)
        main_box.columnconfigure(1, weight=0, minsize=295)
        main_box.rowconfigure(0, weight=1)

        # Левая часть: DataGridView (Treeview)
        grid_frame = tk.Frame(main_box, bg=CARD_BG, relief=tk.SOLID, bd=1)
        grid_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

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
        self.tree.tag_configure("normal", background="#FFFFFF", foreground=TEXT_COLOR)

        # Правая часть: GroupBox Сортировка (фиксированная ширина 295px)
        sort_group = tk.LabelFrame(main_box, text="Сортировка", font=("Segoe UI", 9, "bold"),
                                   bg=CARD_BG, fg=PRIMARY_COLOR, padx=14, pady=10, relief=tk.SOLID, bd=1, width=295)
        sort_group.grid(row=0, column=1, sticky="nsew")
        sort_group.grid_propagate(False)

        tk.Label(sort_group, text="Поле для сортировки:", font=("Segoe UI", 9, "bold"),
                 bg=CARD_BG, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=(0, 4))

        list_frame = tk.Frame(sort_group, bg=CARD_BG)
        list_frame.pack(fill=tk.X, pady=(0, 8))

        self.listbox = tk.Listbox(list_frame, height=6, font=("Segoe UI", 9),
                                  selectmode=tk.SINGLE, relief=tk.SOLID, bd=1)
        lb_vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_vsb.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # Направление сортировки - интерактивные кнопки с индикатором
        tk.Label(sort_group, text="Порядок сортировки:", font=("Segoe UI", 9, "bold"),
                 bg=CARD_BG, fg=TEXT_COLOR, anchor="w").pack(fill=tk.X, pady=(6, 4))

        dir_box = tk.Frame(sort_group, bg=CARD_BG)
        dir_box.pack(fill=tk.X, pady=(0, 4))
        dir_box.columnconfigure(0, weight=1, uniform="dir_btn")
        dir_box.columnconfigure(1, weight=1, uniform="dir_btn")

        self.btn_dir_asc = tk.Button(dir_box, text="▲ По возр.", cursor="hand2", pady=4,
                                     command=lambda: self.set_direction("ASC"))
        self.btn_dir_asc.grid(row=0, column=0, padx=2, sticky="ew")

        self.btn_dir_desc = tk.Button(dir_box, text="▼ По убыв.", cursor="hand2", pady=4,
                                      command=lambda: self.set_direction("DESC"))
        self.btn_dir_desc.grid(row=0, column=1, padx=2, sticky="ew")

        self.lbl_dir_status = tk.Label(sort_group, text="", font=("Segoe UI", 8, "bold"),
                                       bg=CARD_BG, anchor="w")
        self.lbl_dir_status.pack(fill=tk.X, pady=(2, 8))

        # Заметная 3D кнопка запуска сортировки
        self.btn_sort = tk.Button(sort_group, text="Применить сортировку", font=("Segoe UI", 9, "bold"),
                                  bg="#047857", fg="#FFFFFF", activebackground="#065F46", activeforeground="#FFFFFF",
                                  relief=tk.RAISED, bd=2, cursor="hand2", pady=6, command=self.apply_sort)
        self.btn_sort.pack(fill=tk.X, pady=(6, 2))

        # Нижняя панель действий (Фильтр, Поиск, Закрыть)
        bottom_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=10)
        bottom_card.pack(fill=tk.X, padx=16, pady=(6, 12))

        # Ряд 1: Фильтрация
        row_filter = tk.Frame(bottom_card, bg=CARD_BG)
        row_filter.pack(fill=tk.X, pady=3)

        self.lbl_filter = tk.Label(row_filter, text="Поле фильтра:", width=14, anchor="w",
                                   font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
        self.lbl_filter.pack(side=tk.LEFT)

        self.filter_var = tk.StringVar()
        self.cb_filter = ttk.Combobox(row_filter, textvariable=self.filter_var, font=("Segoe UI", 9),
                                      state="readonly", width=36)
        self.cb_filter.pack(side=tk.LEFT, padx=(0, 10))

        btn_filter = tk.Button(row_filter, text="Фильтровать", font=("Segoe UI", 9, "bold"),
                               bg="#ECFDF5", fg="#047857", relief=tk.RAISED, bd=2,
                               cursor="hand2", padx=12, pady=2, command=self.apply_filter)
        btn_filter.pack(side=tk.LEFT, padx=4)

        btn_show_all = tk.Button(row_filter, text="Показать все", font=("Segoe UI", 9),
                                 bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.RAISED, bd=2,
                                 cursor="hand2", padx=12, pady=2, command=self.show_all_records)
        btn_show_all.pack(side=tk.LEFT, padx=4)

        # Ряд 2: Поиск
        row_search = tk.Frame(bottom_card, bg=CARD_BG)
        row_search.pack(fill=tk.X, pady=3)

        lbl_crit = tk.Label(row_search, text="Критерий:", width=14, anchor="w",
                            font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TEXT_COLOR)
        lbl_crit.pack(side=tk.LEFT)

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(row_search, textvariable=self.search_var, font=("Segoe UI", 9), width=38)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.apply_search())

        btn_search = tk.Button(row_search, text="Найти", font=("Segoe UI", 9, "bold"),
                               bg="#ECFDF5", fg=PRIMARY_COLOR, relief=tk.RAISED, bd=2,
                               cursor="hand2", padx=16, pady=2, command=self.apply_search)
        btn_search.pack(side=tk.LEFT, padx=4)

        btn_close = tk.Button(row_search, text="Закрыть", font=("Segoe UI", 9, "bold"),
                              bg="#FEF2F2", fg="#DC2626", relief=tk.RAISED, bd=2,
                              cursor="hand2", padx=16, pady=2, command=self.destroy)
        btn_close.pack(side=tk.RIGHT, padx=4)

        self.status_var = tk.StringVar(value="Готово")
        lbl_status = tk.Label(self, textvariable=self.status_var, font=("Segoe UI", 8),
                              bg=BG_COLOR, fg="#64748B", anchor="w", padx=18)
        lbl_status.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 4))

        self.set_direction("ASC")

    def set_direction(self, direction):
        self.sort_direction = direction
        if direction == "ASC":
            self.btn_dir_asc.config(bg=PRIMARY_COLOR, fg="#FFFFFF", relief=tk.SUNKEN, bd=2, font=("Segoe UI", 9, "bold"))
            self.btn_dir_desc.config(bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.RAISED, bd=1, font=("Segoe UI", 9))
            self.lbl_dir_status.config(text="Включено: по возрастанию (А → Я)", fg=PRIMARY_COLOR)
        else:
            self.btn_dir_desc.config(bg=PRIMARY_COLOR, fg="#FFFFFF", relief=tk.SUNKEN, bd=2, font=("Segoe UI", 9, "bold"))
            self.btn_dir_asc.config(bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.RAISED, bd=1, font=("Segoe UI", 9))
            self.lbl_dir_status.config(text="Включено: по убыванию (Я → А)", fg="#B91C1C")

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

        # Выбираем первое поле по умолчанию
        if cfg["sort_fields"]:
            self.listbox.selection_set(0)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(cfg["query"])
        self.raw_rows = [list(row) for row in cur.fetchall()]
        conn.close()

        self.filtered_rows = list(self.raw_rows)
        self._populate_tree(self.filtered_rows)

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
        pass

    def apply_sort(self):
        sel = self.listbox.curselection()
        if not sel:
            self.listbox.selection_set(0)
            sel = (0,)

        col_idx = sel[0]
        descending = (self.sort_direction == "DESC")

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
