import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection, get_libraries_dict, get_books_dict
from table_view import TableViewForm
from reports import ReportViewerForm

WIN_BG = "#ECE9D8"
HEADER_COLOR = "#000080"
BTN_BG = "#F0EFEA"

class BaseRecordForm(tk.Toplevel):
    def __init__(self, parent, title, table_name, fields_config, on_update_callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("740x510")
        self.configure(bg=WIN_BG)
        self.resizable(False, False)

        self.table_name = table_name
        self.fields_config = fields_config
        self.on_update_callback = on_update_callback

        self.records = []
        self.current_index = 0
        self.is_new_record = False

        self._build_ui(title)
        self.load_records()

    def _build_ui(self, title_text):
        # 1. Верхняя панель навигации (BindingNavigator в стиле WinForms)
        nav_frame = tk.Frame(self, bg="#E6E3D3", relief=tk.RAISED, bd=1)
        nav_frame.pack(fill=tk.X, side=tk.TOP, padx=2, pady=2)

        nav_opt = {"font": ("Tahoma", 8), "bg": BTN_BG, "relief": tk.GROOVE, "bd": 1, "cursor": "hand2"}

        self.btn_nav_first = tk.Button(nav_frame, text="|◀", width=3, command=self.go_first, **nav_opt)
        self.btn_nav_first.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_nav_prev = tk.Button(nav_frame, text="◀", width=3, command=self.go_prev, **nav_opt)
        self.btn_nav_prev.pack(side=tk.LEFT, padx=2, pady=2)

        self.nav_pos_var = tk.StringVar(value="0 из 0")
        self.nav_pos_label = tk.Label(nav_frame, textvariable=self.nav_pos_var, bg="#E6E3D3", font=("Tahoma", 9, "bold"), width=12)
        self.nav_pos_label.pack(side=tk.LEFT, padx=4)

        self.btn_nav_next = tk.Button(nav_frame, text="▶", width=3, command=self.go_next, **nav_opt)
        self.btn_nav_next.pack(side=tk.LEFT, padx=2, pady=2)

        self.btn_nav_last = tk.Button(nav_frame, text="▶|", width=3, command=self.go_last, **nav_opt)
        self.btn_nav_last.pack(side=tk.LEFT, padx=2, pady=2)

        sep = ttk.Separator(nav_frame, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=2)

        tk.Button(nav_frame, text="Добавить", fg="#006600", font=("Tahoma", 8, "bold"),
                  bg=BTN_BG, relief=tk.GROOVE, bd=1, cursor="hand2", padx=6, command=self.add_record).pack(side=tk.LEFT, padx=3, pady=2)

        tk.Button(nav_frame, text="Сохранить", fg="#000099", font=("Tahoma", 8, "bold"),
                  bg=BTN_BG, relief=tk.GROOVE, bd=1, cursor="hand2", padx=6, command=self.save_record).pack(side=tk.LEFT, padx=3, pady=2)

        tk.Button(nav_frame, text="Удалить", fg="#CC0000", font=("Tahoma", 8, "bold"),
                  bg=BTN_BG, relief=tk.GROOVE, bd=1, cursor="hand2", padx=6, command=self.delete_record).pack(side=tk.LEFT, padx=3, pady=2)

        # Кнопки быстрого перехода ЛР 6: Таблица и Отчет
        tk.Button(nav_frame, text="Отчёт", font=("Tahoma", 8, "bold"), bg="#E2F5E8", fg="#006600",
                  relief=tk.GROOVE, bd=1, cursor="hand2", padx=10,
                  command=self.open_report).pack(side=tk.RIGHT, padx=4, pady=2)

        tk.Button(nav_frame, text="Таблица", font=("Tahoma", 8, "bold"), bg="#E2EBF5", fg=HEADER_COLOR,
                  relief=tk.GROOVE, bd=1, cursor="hand2", padx=10,
                  command=self.open_table).pack(side=tk.RIGHT, padx=4, pady=2)

        # 2. Заголовок формы (синий крупный заголовок WinForms)
        lbl_title = tk.Label(self, text=title_text, font=("Tahoma", 14, "bold"), fg=HEADER_COLOR, bg=WIN_BG)
        lbl_title.pack(pady=(14, 16))

        # 3. Область полей ввода
        self.fields_frame = tk.Frame(self, bg=WIN_BG)
        self.fields_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=4)

        self.widgets = {}
        for row_idx, cfg in enumerate(self.fields_config):
            field_name = cfg["name"]
            label_text = cfg["label"]
            field_type = cfg.get("type", "entry")

            lbl = tk.Label(self.fields_frame, text=label_text + ":", bg=WIN_BG, font=("Tahoma", 9, "bold"), width=22, anchor="e")
            lbl.grid(row=row_idx, column=0, sticky="e", padx=(0, 14), pady=7)

            if field_type == "entry":
                var = tk.StringVar()
                entry = tk.Entry(self.fields_frame, textvariable=var, font=("Tahoma", 9), width=42, relief=tk.SUNKEN, bd=1)
                if cfg.get("readonly", False):
                    entry.configure(state="readonly")
                entry.grid(row=row_idx, column=1, sticky="w", pady=7)
                self.widgets[field_name] = {"widget": entry, "var": var, "cfg": cfg}

            elif field_type == "combobox":
                var = tk.StringVar()
                cb = ttk.Combobox(self.fields_frame, textvariable=var, font=("Tahoma", 9),
                                  values=cfg.get("values", []), state="readonly", width=40)
                cb.grid(row=row_idx, column=1, sticky="w", pady=7)
                self.widgets[field_name] = {"widget": cb, "var": var, "cfg": cfg}

        # 4. Нижний блок: 7 кнопок ровно в один ряд (широкий и просторный)
        bottom_frame = tk.Frame(self, bg=WIN_BG, relief=tk.GROOVE, bd=2)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=(6, 14))

        btn_row = tk.Frame(bottom_frame, bg=WIN_BG)
        btn_row.pack(fill=tk.X, padx=8, pady=8)

        buttons = [
            ("Первая", self.go_first, False),
            ("Предыдущая", self.go_prev, False),
            ("Добавить", self.add_record, True),
            ("Сохранить", self.save_record, True),
            ("Удалить", self.delete_record, True),
            ("Следующая", self.go_next, False),
            ("Последняя", self.go_last, False),
        ]

        for col_idx, (btext, bcmd, is_bold) in enumerate(buttons):
            btn_row.columnconfigure(col_idx, weight=1)
            f_weight = "bold" if is_bold else "normal"
            tk.Button(
                btn_row,
                text=btext,
                command=bcmd,
                bg=BTN_BG,
                font=("Tahoma", 9, f_weight),
                relief=tk.RAISED,
                bd=1,
                cursor="hand2",
                pady=4
            ).grid(row=0, column=col_idx, padx=3, sticky="ew")

    def open_table(self):
        TableViewForm(self, initial_table=self.table_name)

    def open_report(self):
        ReportViewerForm(self)

    def load_records(self):
        conn = get_connection()
        query = f"SELECT * FROM {self.table_name} ORDER BY 1"
        self.records = [dict(row) for row in conn.execute(query).fetchall()]
        conn.close()

        if self.records:
            self.current_index = 0
            self.show_record(self.current_index)
        else:
            self.add_record()

    def show_record(self, idx):
        if not self.records or idx < 0 or idx >= len(self.records):
            return
        self.current_index = idx
        self.is_new_record = False
        rec = self.records[idx]

        for name, comp in self.widgets.items():
            val = rec.get(name, "")
            cfg = comp["cfg"]
            if cfg.get("type") == "combobox" and "key_map" in cfg:
                rev_map = cfg.get("rev_map", {})
                comp["var"].set(rev_map.get(val, str(val)))
            else:
                comp["var"].set("" if val is None else str(val))

        total = len(self.records)
        self.nav_pos_var.set(f"{idx + 1} из {total}")

    def go_first(self):
        if self.records:
            self.show_record(0)

    def go_prev(self):
        if self.current_index > 0:
            self.show_record(self.current_index - 1)

    def go_next(self):
        if self.current_index < len(self.records) - 1:
            self.show_record(self.current_index + 1)

    def go_last(self):
        if self.records:
            self.show_record(len(self.records) - 1)

    def add_record(self):
        self.is_new_record = True
        for name, comp in self.widgets.items():
            if comp["cfg"].get("readonly"):
                comp["var"].set("(Авто)")
            else:
                comp["var"].set("")
        total = len(self.records)
        self.nav_pos_var.set(f"{total + 1} из {total + 1}")

    def save_record(self):
        values = {}
        for name, comp in self.widgets.items():
            cfg = comp["cfg"]
            if cfg.get("readonly"):
                continue
            raw_val = comp["var"].get().strip()
            if not raw_val:
                messagebox.showwarning("Ошибка ввода", f"Поле '{cfg['label']}' не может быть пустым!", parent=self)
                return

            if cfg.get("type") == "combobox" and "key_map" in cfg:
                key_map = cfg["key_map"]
                if raw_val not in key_map:
                    messagebox.showwarning("Ошибка выбора", f"Выберите значение для '{cfg['label']}' из списка!", parent=self)
                    return
                values[name] = key_map[raw_val]
            else:
                if cfg.get("datatype") == "int":
                    try:
                        values[name] = int(raw_val)
                    except ValueError:
                        messagebox.showwarning("Ошибка типа данных", f"Поле '{cfg['label']}' должно быть числовым!", parent=self)
                        return
                else:
                    values[name] = raw_val

        conn = get_connection()
        cur = conn.cursor()

        try:
            if self.is_new_record:
                cols = list(values.keys())
                placeholders = ["?"] * len(cols)
                sql = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
                cur.execute(sql, list(values.values()))
                conn.commit()
                messagebox.showinfo("Успех", "Запись успешно сохранена!", parent=self)
            else:
                rec = self.records[self.current_index]
                pk_name = self.fields_config[0]["name"]
                pk_val = rec[pk_name]
                set_clause = ", ".join([f"{k} = ?" for k in values.keys()])
                sql = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_name} = ?"
                cur.execute(sql, list(values.values()) + [pk_val])
                conn.commit()
                messagebox.showinfo("Успех", "Изменения успешно сохранены!", parent=self)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось сохранить запись: {e}", parent=self)
            conn.close()
            return

        conn.close()
        self.load_records()
        if self.on_update_callback:
            self.on_update_callback()

    def delete_record(self):
        if not self.records or self.is_new_record:
            return

        rec = self.records[self.current_index]
        pk_name = self.fields_config[0]["name"]
        pk_val = rec[pk_name]

        if not messagebox.askyesno("Подтверждение", f"Удалить текущую запись (Код: {pk_val})?", parent=self):
            return

        conn = get_connection()
        try:
            conn.execute(f"DELETE FROM {self.table_name} WHERE {pk_name} = ?", (pk_val,))
            conn.commit()
            messagebox.showinfo("Успех", "Запись успешно удалена!", parent=self)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись: {e}", parent=self)
        finally:
            conn.close()

        self.load_records()
        if self.on_update_callback:
            self.on_update_callback()

class BooksForm(BaseRecordForm):
    def __init__(self, parent, on_update_callback=None):
        fields = [
            {"name": "shifr", "label": "Шифр книги (PK)", "type": "entry"},
            {"name": "author", "label": "Автор произведения", "type": "entry"},
            {"name": "title", "label": "Наименование книги", "type": "entry"},
            {"name": "publisher", "label": "Издательство", "type": "entry"},
            {"name": "year", "label": "Год издания", "type": "entry", "datatype": "int"},
        ]
        super().__init__(parent, "Таблица \"Книги\"", "books", fields, on_update_callback)

class LibrariesForm(BaseRecordForm):
    def __init__(self, parent, on_update_callback=None):
        fields = [
            {"name": "number", "label": "Номер филиала (PK)", "type": "entry", "datatype": "int"},
            {"name": "address", "label": "Адрес филиала", "type": "entry"},
            {"name": "phone", "label": "Номер телефона", "type": "entry"},
        ]
        super().__init__(parent, "Таблица \"Библиотеки\"", "libraries", fields, on_update_callback)

class CopiesForm(BaseRecordForm):
    def __init__(self, parent, on_update_callback=None):
        lib_map = get_libraries_dict()
        lib_key_map = {v: k for k, v in lib_map.items()}

        books_map = get_books_dict()
        books_key_map = {v: k for k, v in books_map.items()}

        fields = [
            {"name": "id", "label": "Код экземпляра (ID)", "type": "entry", "readonly": True},
            {"name": "lib_number", "label": "Филиал библиотеки", "type": "combobox",
             "values": list(lib_map.values()), "key_map": lib_key_map, "rev_map": lib_map},
            {"name": "book_shifr", "label": "Книга фонда", "type": "combobox",
             "values": list(books_map.values()), "key_map": books_key_map, "rev_map": books_map},
            {"name": "hall", "label": "Читальный зал", "type": "combobox",
             "values": ["Зал художественной литературы", "Зал классики", "Зал редких изданий", "Читальный зал №1", "Абонементный зал"]},
        ]
        super().__init__(parent, "Таблица \"Экземпляры\"", "copies", fields, on_update_callback)
