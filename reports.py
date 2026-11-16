import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
from database import get_connection

BG_COLOR = "#F1F5F9"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_COLOR = "#2563EB"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"

class ReportViewerForm(tk.Toplevel):
    def __init__(self, parent, default_report_index=1):
        super().__init__(parent)
        self.title("Генератор и просмотрщик отчетов — Лабораторная работа №6")
        self.geometry("860x650")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.current_report_idx = default_report_index
        self._build_ui()
        self.generate_report(self.current_report_idx)

    def _build_ui(self):
        # 1. Верхняя панель выбора отчета (4 отчета)
        top_bar = tk.Frame(self, bg=PRIMARY_COLOR, padx=16, pady=12)
        top_bar.pack(fill=tk.X)

        lbl_hdr = tk.Label(top_bar, text="ПОСТРОЕНИЕ И ПРОСМОТР ОТЧЕТОВ БАЗЫ ДАННЫХ",
                           font=("Segoe UI", 12, "bold"), fg="white", bg=PRIMARY_COLOR)
        lbl_hdr.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(top_bar, bg=PRIMARY_COLOR)
        btn_box.pack(fill=tk.X)

        self.btn_rep1 = tk.Button(btn_box, text="1. Каталог фонда", font=("Segoe UI", 9, "bold"),
                                  bg="#3B82F6", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(1))
        self.btn_rep1.pack(side=tk.LEFT, padx=3)

        self.btn_rep2 = tk.Button(btn_box, text="2. Филиалы сети", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(2))
        self.btn_rep2.pack(side=tk.LEFT, padx=3)

        self.btn_rep3 = tk.Button(btn_box, text="3. Экземпляры по залам", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(3))
        self.btn_rep3.pack(side=tk.LEFT, padx=3)

        self.btn_rep4 = tk.Button(btn_box, text="4. Сводный по издательствам", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(4))
        self.btn_rep4.pack(side=tk.LEFT, padx=3)

        # 2. Область отображения отчета (стилизованный лист формата А4 / отчетный документ)
        doc_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        doc_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        # Заголовок документа отчета
        self.lbl_rep_title = tk.Label(doc_card, text="", font=("Segoe UI", 13, "bold"),
                                      bg=CARD_BG, fg=PRIMARY_COLOR)
        self.lbl_rep_title.pack(anchor="w", padx=16, pady=(12, 2))

        self.lbl_rep_meta = tk.Label(doc_card, text="", font=("Segoe UI", 9),
                                     bg=CARD_BG, fg="#64748B")
        self.lbl_rep_meta.pack(anchor="w", padx=16, pady=(0, 8))

        # Таблица данных отчета
        tree_frame = tk.Frame(doc_card, bg=CARD_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.tree = ttk.Treeview(tree_frame, show="headings", selectmode="none")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Report.Treeview", background="#FFFFFF", foreground=TEXT_COLOR,
                        rowheight=24, font=("Segoe UI", 9))
        style.configure("Report.Treeview.Heading", background="#E2E8F0", foreground=TEXT_COLOR,
                        font=("Segoe UI", 9, "bold"))
        self.tree.configure(style="Report.Treeview")

        # Итоговая строка
        self.lbl_summary = tk.Label(doc_card, text="", font=("Segoe UI", 9, "bold"),
                                    bg="#F8FAFC", fg=PRIMARY_COLOR, anchor="e", padx=16, pady=6,
                                    relief=tk.GROOVE)
        self.lbl_summary.pack(fill=tk.X, side=tk.BOTTOM)

        # 3. Нижняя панель действий (Экспорт, Печать, Закрыть)
        act_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=8)
        act_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Button(act_card, text="Печать / Предпросмотр", font=("Segoe UI", 9),
                  bg="#F1F5F9", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1, cursor="hand2", padx=10,
                  command=self.print_preview).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Экспорт отчета в HTML", font=("Segoe UI", 9),
                  bg="#ECFDF5", fg="#047857", relief=tk.GROOVE, bd=1, cursor="hand2", padx=10,
                  command=self.export_html).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Экспорт в TXT", font=("Segoe UI", 9),
                  bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1, cursor="hand2", padx=10,
                  command=self.export_txt).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Закрыть", font=("Segoe UI", 9, "bold"),
                  bg="#FEF2F2", fg="#DC2626", relief=tk.GROOVE, bd=1, cursor="hand2", padx=14,
                  command=self.destroy).pack(side=tk.RIGHT, padx=4)

    def _update_button_styles(self, active_idx):
        btns = [self.btn_rep1, self.btn_rep2, self.btn_rep3, self.btn_rep4]
        for i, b in enumerate(btns, start=1):
            if i == active_idx:
                b.configure(bg="#2563EB", relief=tk.SUNKEN)
            else:
                b.configure(bg="#1E40AF", relief=tk.FLAT)

    def generate_report(self, report_idx):
        self.current_report_idx = report_idx
        self._update_button_styles(report_idx)

        for col in self.tree.get_children():
            self.tree.delete(col)

        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn = get_connection()
        cur = conn.cursor()

        if report_idx == 1:
            title = "ОТЧЕТ №1: Каталог книжного фонда библиотеки"
            meta = f"Формирование отчета: {now_str} • Параметры: полный каталог фонда"
            cols = [("shifr", "Шифр книги", 110), ("author", "Автор", 200),
                    ("title", "Наименование произведения", 260), ("publisher", "Издательство", 140),
                    ("year", "Год издания", 100)]
            cur.execute("SELECT shifr, author, title, publisher, year FROM books ORDER BY author, year")
            rows = cur.fetchall()
            summary = f"ИТОГО ПО КАТАЛОГУ: {len(rows)} наименований книг"

        elif report_idx == 2:
            title = "ОТЧЕТ №2: Справочник библиотечных отделений и филиалов"
            meta = f"Формирование отчета: {now_str} • Параметры: филиалы сети с подсчетом фонда"
            cols = [("num", "Номер филиала", 120), ("addr", "Фактический адрес", 320),
                    ("phone", "Контактный телефон", 180), ("cnt", "Экземпляров на хранении", 180)]
            cur.execute("""
            SELECT l.number, l.address, l.phone, COUNT(c.id)
            FROM libraries l
            LEFT JOIN copies c ON l.number = c.lib_number
            GROUP BY l.number, l.address, l.phone
            ORDER BY l.number
            """)
            rows = cur.fetchall()
            total_copies = sum(r[3] for r in rows)
            summary = f"ИТОГО: {len(rows)} библиотечных филиалов | Всего прикреплено экземпляров: {total_copies}"

        elif report_idx == 3:
            title = "ОТЧЕТ №3: Ведомость распределения экземпляров по залам и филиалам"
            meta = f"Формирование отчета: {now_str} • Параметры: учет поэкземплярного размещения"
            cols = [("id", "Код", 60), ("lib", "Филиал библиотеки", 160), ("shifr", "Шифр книги", 100),
                    ("title", "Название книги", 220), ("author", "Автор", 180), ("hall", "Читальный зал", 180)]
            cur.execute("""
            SELECT c.id, 'Филиал №' || c.lib_number, c.book_shifr, b.title, b.author, c.hall
            FROM copies c
            JOIN books b ON c.book_shifr = b.shifr
            ORDER BY c.lib_number, c.id
            """)
            rows = cur.fetchall()
            summary = f"ИТОГО В ВЕДОМОСТИ: {len(rows)} экземпляров книг на хранении"

        elif report_idx == 4:
            title = "ОТЧЕТ №4: Сводный статистический отчет по издательствам"
            meta = f"Формирование отчета: {now_str} • Параметры: группировка и аналитика фонда"
            cols = [("pub", "Издательство", 240), ("cnt", "Число наименований", 180),
                    ("min_yr", "Самое раннее издание", 180), ("max_yr", "Самое позднее издание", 180)]
            cur.execute("""
            SELECT publisher, COUNT(*), MIN(year), MAX(year)
            FROM books
            GROUP BY publisher
            ORDER BY COUNT(*) DESC
            """)
            rows = cur.fetchall()
            total_b = sum(r[1] for r in rows)
            summary = f"ИТОГО: {len(rows)} издательств в фонде | Всего книг: {total_b}"

        conn.close()

        self.lbl_rep_title.config(text=title)
        self.lbl_rep_meta.config(text=meta)
        self.lbl_summary.config(text=summary)

        self.current_cols = cols
        self.current_rows = rows
        self.current_title = title
        self.current_summary = summary

        self.tree["columns"] = [c[0] for c in cols]
        for cid, cname, width in cols:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor="w")

        for idx, r in enumerate(rows):
            self.tree.insert("", "end", iid=str(idx), values=[str(v) for v in r])

    def print_preview(self):
        msg = (f"Предварительный просмотр печати:\n\n"
               f"{self.current_title}\n"
               f"{self.lbl_rep_meta.cget('text')}\n\n"
               f"Строк в документе: {len(self.current_rows)}\n"
               f"{self.current_summary}\n\n"
               f"Документ готов к выводу на системный принтер.")
        messagebox.showinfo("Печать отчета", msg, parent=self)

    def export_html(self):
        fpath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".html",
            filetypes=[("HTML файлы", "*.html"), ("Все файлы", "*.*")],
            initialfile=f"отчет_{self.current_report_idx}.html"
        )
        if not fpath:
            return

        headers_html = "".join([f"<th style='border:1px solid #CBD5E1; padding:8px; background:#1E3A8A; color:white;'>{c[1]}</th>" for c in self.current_cols])
        rows_html = ""
        for idx, r in enumerate(self.current_rows):
            bg = "#F8FAFC" if idx % 2 == 1 else "#FFFFFF"
            cells = "".join([f"<td style='border:1px solid #CBD5E1; padding:6px;'>{v}</td>" for v in r])
            rows_html += f"<tr style='background:{bg};'>{cells}</tr>"

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{self.current_title}</title>
    <style>
        body {{ font-family: Segoe UI, Arial, sans-serif; margin: 30px; color: #0F172A; }}
        h2 {{ color: #1E3A8A; margin-bottom: 4px; }}
        .meta {{ color: #64748B; font-size: 13px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
        .summary {{ margin-top: 20px; font-weight: bold; color: #1E3A8A; }}
    </style>
</head>
<body>
    <h2>{self.current_title}</h2>
    <div class="meta">{self.lbl_rep_meta.cget('text')}</div>
    <table>
        <thead><tr>{headers_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    <div class="summary">{self.current_summary}</div>
</body>
</html>"""

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html_content)
        messagebox.showinfo("Экспорт завершен", f"Отчет успешно сохранен в файл:\n{fpath}", parent=self)

    def export_txt(self):
        fpath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            initialfile=f"отчет_{self.current_report_idx}.txt"
        )
        if not fpath:
            return

        lines = [
            self.current_title,
            self.lbl_rep_meta.cget('text'),
            "=" * 70,
            " | ".join([c[1] for c in self.current_cols]),
            "-" * 70
        ]
        for r in self.current_rows:
            lines.append(" | ".join([str(v) for v in r]))
        lines.append("=" * 70)
        lines.append(self.current_summary)

        with open(fpath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Экспорт завершен", f"Отчет успешно сохранен в файл:\n{fpath}", parent=self)
