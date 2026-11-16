import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import get_connection, get_libraries_dict, get_books_dict
from table_view import TableViewForm
from reports import ReportViewerForm

BG_MAIN = "#F1F5F9"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_COLOR = "#2563EB"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"
BTN_HOVER = "#DBEAFE"

class BaseModernRecordForm(tk.Toplevel):
    def __init__(self, parent, title, table_name, fields_config, on_update_callback=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("620x540")
        self.configure(bg=BG_MAIN)
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
        # 1. Верхний бар навигации (BindingNavigator)
        nav_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        nav_card.pack(fill=tk.X, padx=14, pady=(12, 6))

        btn_bar = tk.Frame(nav_card, bg=CARD_BG)
        btn_bar.pack(fill=tk.X, padx=8, pady=6)

        nav_btn_opt = {
            "font": ("Segoe UI", 9, "bold"),
            "bg": "#F8FAFC",
            "fg": TEXT_COLOR,
            "activebackground": BTN_HOVER,
            "relief": tk.FLAT,
            "bd": 1,
            "cursor": "hand2"
        }

        self.btn_first = tk.Button(btn_bar, text="|◀", width=3, command=self.go_first, **nav_btn_opt)
        self.btn_first.pack(side=tk.LEFT, padx=2)

        self.btn_prev = tk.Button(btn_bar, text="◀", width=3, command=self.go_prev, **nav_btn_opt)
        self.btn_prev.pack(side=tk.LEFT, padx=2)

        self.nav_pos_var = tk.StringVar(value="0 из 0")
        pos_badge = tk.Label(btn_bar, textvariable=self.nav_pos_var, bg="#EFF6FF", fg=ACCENT_COLOR,
                             font=("Segoe UI", 9, "bold"), padx=10, pady=2, relief=tk.GROOVE)
        pos_badge.pack(side=tk.LEFT, padx=6)

        self.btn_next = tk.Button(btn_bar, text="▶", width=3, command=self.go_next, **nav_btn_opt)
        self.btn_next.pack(side=tk.LEFT, padx=2)

        self.btn_last = tk.Button(btn_bar, text="▶|", width=3, command=self.go_last, **nav_btn_opt)
        self.btn_last.pack(side=tk.LEFT, padx=2)

        sep = tk.Frame(btn_bar, width=2, bg=BORDER_COLOR)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=2)

        tk.Button(btn_bar, text="Добавить", font=("Segoe UI", 9, "bold"), bg="#ECFDF5", fg="#047857",
                  relief=tk.FLAT, cursor="hand2", padx=8, command=self.add_record).pack(side=tk.LEFT, padx=3)

        tk.Button(btn_bar, text="Сохранить", font=("Segoe UI", 9, "bold"), bg="#F0FDF4", fg=PRIMARY_COLOR,
                  relief=tk.FLAT, cursor="hand2", padx=8, command=self.save_record).pack(side=tk.LEFT, padx=3)

        tk.Button(btn_bar, text="Удалить", font=("Segoe UI", 9, "bold"), bg="#FEF2F2", fg="#DC2626",
                  relief=tk.FLAT, cursor="hand2", padx=8, command=self.delete_record).pack(side=tk.LEFT, padx=3)

        # Кнопки быстрого перехода: Таблица и Отчёт (по методичке Рис. 11.18, 12.19)
        tk.Button(btn_bar, text="Отчёт", font=("Segoe UI", 9, "bold"), bg="#EFF6FF", fg=ACCENT_COLOR,
                  relief=tk.GROOVE, bd=1, cursor="hand2", padx=8,
                  command=self.open_report).pack(side=tk.RIGHT, padx=3)

        tk.Button(btn_bar, text="Таблица", font=("Segoe UI", 9, "bold"), bg="#F8FAFC", fg=PRIMARY_COLOR,
                  relief=tk.GROOVE, bd=1, cursor="hand2", padx=8,
                  command=self.open_table).pack(side=tk.RIGHT, padx=3)

        # 2. Карточка формы ввода данных
        form_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        form_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        header_lbl = tk.Label(form_card, text=title_text, font=("Segoe UI", 12, "bold"),
                              bg=CARD_BG, fg=PRIMARY_COLOR)
        header_lbl.pack(anchor="w", padx=16, pady=(12, 10))

        fields_box = tk.Frame(form_card, bg=CARD_BG)
        fields_box.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.inputs = {}
        for row_idx, cfg in enumerate(self.fields_config):
            field_name = cfg["name"]
            label_text = cfg["label"]
            field_type = cfg.get("type", "entry")

            lbl = tk.Label(fields_box, text=label_text, font=("Segoe UI", 9, "bold"),
                           bg=CARD_BG, fg=TEXT_COLOR, anchor="w")
            lbl.grid(row=row_idx, column=0, sticky="w", pady=6, padx=(0, 10))

            if field_type == "entry":
                var = tk.StringVar()
                entry = ttk.Entry(fields_box, textvariable=var, font=("Segoe UI", 10), width=34)
                if cfg.get("readonly", False):
                    entry.configure(state="readonly")
                entry.grid(row=row_idx, column=1, sticky="ew", pady=6)
                self.inputs[field_name] = {"widget": entry, "var": var, "cfg": cfg}

            elif field_type == "combobox":
                var = tk.StringVar()
                cb = ttk.Combobox(fields_box, textvariable=var, font=("Segoe UI", 9),
                                  values=cfg.get("values", []), state="readonly", width=32)
                cb.grid(row=row_idx, column=1, sticky="ew", pady=6)
                self.inputs[field_name] = {"widget": cb, "var": var, "cfg": cfg}

            fields_box.columnconfigure(1, weight=1)

        # Статусная плашка
        self.status_var = tk.StringVar(value="Готово")
        status_bar = tk.Label(form_card, textvariable=self.status_var, font=("Segoe UI", 8),
                              bg="#F8FAFC", fg="#64748B", anchor="w", padx=10, pady=4)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # 3. Нижняя панель действий (Классические кнопки в один ряд через grid)
        action_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        action_card.pack(fill=tk.X, padx=14, pady=(6, 12))

        btn_row = tk.Frame(action_card, bg=CARD_BG)
        btn_row.pack(fill=tk.X, padx=8, pady=8)

        buttons = [
            ("Первая", self.go_first, "#F8FAFC", TEXT_COLOR, False),
            ("Предыдущая", self.go_prev, "#F8FAFC", TEXT_COLOR, False),
            ("Добавить", self.add_record, "#ECFDF5", "#047857", True),
            ("Сохранить", self.save_record, "#F0FDF4", PRIMARY_COLOR, True),
            ("Удалить", self.delete_record, "#FEF2F2", "#DC2626", True),
            ("Следующая", self.go_next, "#F8FAFC", TEXT_COLOR, False),
            ("Последняя", self.go_last, "#F8FAFC", TEXT_COLOR, False),
        ]

        for col_idx, (btext, bcmd, bg_col, fg_col, is_bold) in enumerate(buttons):
            btn_row.columnconfigure(col_idx, weight=1)
            f_weight = "bold" if is_bold else "normal"
            tk.Button(btn_row, text=btext, command=bcmd, bg=bg_col, fg=fg_col,
                      font=("Segoe UI", 9, f_weight), activebackground=BTN_HOVER,
                      relief=tk.GROOVE, bd=1, cursor="hand2", pady=4
                      ).grid(row=0, column=col_idx, padx=2, sticky="ew")

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

        for name, comp in self.inputs.items():
            val = rec.get(name, "")
            cfg = comp["cfg"]
            if cfg.get("type") == "combobox" and "key_map" in cfg:
                rev_map = cfg.get("rev_map", {})
                comp["var"].set(rev_map.get(val, str(val)))
            else:
                comp["var"].set("" if val is None else str(val))

        total = len(self.records)
        self.nav_pos_var.set(f"{idx + 1} из {total}")
        self.status_var.set(f"Запись {idx + 1} из {total} (Все изменения сохранены)")

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
        for name, comp in self.inputs.items():
            if comp["cfg"].get("readonly"):
                comp["var"].set("(Авто)")
            else:
                comp["var"].set("")
        total = len(self.records)
        self.nav_pos_var.set(f"{total + 1} из {total + 1}")
        self.status_var.set("Режим добавления новой записи (Заполните поля и нажмите 'Сохранить')")

    def save_record(self):
        values = {}
        for name, comp in self.inputs.items():
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
                        messagebox.showwarning("Ошибка типа данных", f"Поле '{cfg['label']}' должно быть целым числом!", parent=self)
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
                messagebox.showinfo("Успех", "Новая запись успешно сохранена!", parent=self)
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

class BooksForm(BaseModernRecordForm):
    def __init__(self, parent, on_update_callback=None):
        fields = [
            {"name": "shifr", "label": "Шифр книги (PK):", "type": "entry"},
            {"name": "author", "label": "Автор книги:", "type": "entry"},
            {"name": "title", "label": "Наименование книги:", "type": "entry"},
            {"name": "publisher", "label": "Издательство:", "type": "entry"},
            {"name": "year", "label": "Год издания:", "type": "entry", "datatype": "int"},
        ]
        super().__init__(parent, "Книги — Каталог книжного фонда", "books", fields, on_update_callback)

class LibrariesForm(BaseModernRecordForm):
    def __init__(self, parent, on_update_callback=None):
        fields = [
            {"name": "number", "label": "Номер филиала (PK):", "type": "entry", "datatype": "int"},
            {"name": "address", "label": "Фактический адрес:", "type": "entry"},
            {"name": "phone", "label": "Номер телефона:", "type": "entry"},
        ]
        super().__init__(parent, "Библиотеки — Справочник филиалов", "libraries", fields, on_update_callback)

class CopiesForm(BaseModernRecordForm):
    def __init__(self, parent, on_update_callback=None):
        lib_map = get_libraries_dict()
        lib_key_map = {v: k for k, v in lib_map.items()}

        books_map = get_books_dict()
        books_key_map = {v: k for k, v in books_map.items()}

        fields = [
            {"name": "id", "label": "Код экземпляра (ID):", "type": "entry", "readonly": True},
            {"name": "lib_number", "label": "Филиал библиотеки (FK):", "type": "combobox",
             "values": list(lib_map.values()), "key_map": lib_key_map, "rev_map": lib_map},
            {"name": "book_shifr", "label": "Книга фонда (FK):", "type": "combobox",
             "values": list(books_map.values()), "key_map": books_key_map, "rev_map": books_map},
            {"name": "hall", "label": "Читальный зал:", "type": "combobox",
             "values": ["Зал художественной литературы", "Зал классики", "Зал поэзии", "Зал прозы", "Зал редких изданий", "Читальный зал №1", "Абонементный зал"]},
        ]
        super().__init__(parent, "Экземпляры — Поэкземплярный учет", "copies", fields, on_update_callback)
