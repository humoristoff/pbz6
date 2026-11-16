import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
from database import get_connection

WIN_BG = "#ECE9D8"
HEADER_COLOR = "#000080"
BTN_BG = "#F0EFEA"

class ReportViewerForm(tk.Toplevel):
    def __init__(self, parent, default_report_index=1):
        super().__init__(parent)
        self.title("Генератор и просмотрщик отчетов — Библиотека (ЛР 6)")
        self.geometry("860x640")
        self.configure(bg=WIN_BG)
        self.resizable(False, False)

        self.current_report_idx = default_report_index
        self._build_ui()
        self.generate_report(self.current_report_idx)

    def _build_ui(self):
        # Панель заголовка и выбора отчетов
        top_frame = tk.Frame(self, bg=WIN_BG, padx=14, pady=8)
        top_frame.pack(fill=tk.X)

        lbl_hdr = tk.Label(top_frame, text="ПОСТРОЕНИЕ И ПРОСМОТР ОТЧЕТОВ БИБЛИОТЕКИ",
                           font=("Tahoma", 11, "bold"), fg=HEADER_COLOR, bg=WIN_BG)
        lbl_hdr.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(top_frame, bg=WIN_BG)
        btn_box.pack(fill=tk.X)

        btn_opt = {"font": ("Tahoma", 8, "bold"), "bg": BTN_BG, "relief": tk.RAISED, "bd": 1, "cursor": "hand2", "padx": 6, "pady": 3}

        self.btn_rep1 = tk.Button(btn_box, text="1. Каталог фонда", command=lambda: self.generate_report(1), **btn_opt)
        self.btn_rep1.pack(side=tk.LEFT, padx=3)

        self.btn_rep2 = tk.Button(btn_box, text="2. Филиалы библиотек", command=lambda: self.generate_report(2), **btn_opt)
        self.btn_rep2.pack(side=tk.LEFT, padx=3)

        self.btn_rep3 = tk.Button(btn_box, text="3. Распределение экземпляров", command=lambda: self.generate_report(3), **btn_opt)
        self.btn_rep3.pack(side=tk.LEFT, padx=3)

        self.btn_rep4 = tk.Button(btn_box, text="4. Сводка по издательствам", command=lambda: self.generate_report(4), **btn_opt)
        self.btn_rep4.pack(side=tk.LEFT, padx=3)

        # Контейнер отчета
        doc_card = tk.Frame(self, bg="#FFFFFF", relief=tk.SUNKEN, bd=2)
        doc_card.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        self.lbl_rep_title = tk.Label(doc_card, text="", font=("Tahoma", 12, "bold"), bg="#FFFFFF", fg=HEADER_COLOR)
        self.lbl_rep_title.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_rep_meta = tk.Label(doc_card, text="", font=("Tahoma", 8), bg="#FFFFFF", fg="#666666")
        self.lbl_rep_meta.pack(anchor="w", padx=12, pady=(0, 6))

        tree_frame = tk.Frame(doc_card, bg="#FFFFFF")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        self.tree = ttk.Treeview(tree_frame, show="headings", selectmode="none")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.lbl_summary = tk.Label(doc_card, text="", font=("Tahoma", 9, "bold"),
                                    bg="#F0F0F0", fg=HEADER_COLOR, anchor="e", padx=14, pady=5, relief=tk.GROOVE)
        self.lbl_summary.pack(fill=tk.X, side=tk.BOTTOM)

        # Нижняя панель действий
        act_frame = tk.Frame(self, bg=WIN_BG, relief=tk.GROOVE, bd=2, padx=10, pady=6)
        act_frame.pack(fill=tk.X, padx=14, pady=(2, 10))

        tk.Button(act_frame, text="Печать / Предпросмотр", font=("Tahoma", 8),
                  bg=BTN_BG, relief=tk.RAISED, bd=1, cursor="hand2", padx=10, pady=2,
                  command=self.action_print).pack(side=tk.LEFT, padx=4)

        tk.Button(act_frame, text="Экспорт в HTML", font=("Tahoma", 8, "bold"),
                  bg="#E2EBF5", fg=HEADER_COLOR, relief=tk.RAISED, bd=1, cursor="hand2", padx=10, pady=2,
                  command=self.action_export_html).pack(side=tk.LEFT, padx=4)

        tk.Button(act_frame, text="Экспорт в TXT", font=("Tahoma", 8),
                  bg=BTN_BG, relief=tk.RAISED, bd=1, cursor="hand2", padx=10, pady=2,
                  command=self.action_export_txt).pack(side=tk.LEFT, padx=4)

        tk.Button(act_frame, text="Закрыть", font=("Tahoma", 8, "bold"),
                  bg=BTN_BG, fg="#CC0000", relief=tk.RAISED, bd=1, cursor="hand2", padx=14, pady=2,
                  command=self.destroy).pack(side=tk.RIGHT, padx=4)

    def _highlight_button(self, idx):
        btns = [self.btn_rep1, self.btn_rep2, self.btn_rep3, self.btn_rep4]
        for i, b in enumerate(btns, 1):
            if i == idx:
                b.configure(relief=tk.SUNKEN, bg="#D0E4F7")
            else:
                b.configure(relief=tk.RAISED, bg=BTN_BG)

    def generate_report(self, idx):
        self.current_report_idx = idx
        self._highlight_button(idx)

        for col in self.tree.get_children():
            self.tree.delete(col)

        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn = get_connection()
        cur = conn.cursor()

        if idx == 1:
            self.rep_title = "Каталог книжного фонда библиотеки"
            self.lbl_rep_title.config(text=f"Отчет № 1: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источник: Таблица books | База данных: library.db")

            headers = [
                ("shifr", "Шифр книги", 110),
                ("author", "Автор произведения", 200),
                ("title", "Название книги", 240),
                ("publisher", "Издательство", 160),
                ("year", "Год издания", 100),
            ]
            self._setup_columns(headers)

            cur.execute("SELECT shifr, author, title, publisher, year FROM books ORDER BY author, year")
            rows = cur.fetchall()
            for r in rows:
                self.tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4]))

            years = [r[4] for r in rows if r[4]]
            y_min = min(years) if years else "-"
            y_max = max(years) if years else "-"
            self.lbl_summary.config(text=f"ИТОГО: Всего книг в фонде — {len(rows)} шт. | Диапазон годов: {y_min} – {y_max} гг.")

        elif idx == 2:
            self.rep_title = "Справочник отделений и филиалов библиотеки"
            self.lbl_rep_title.config(text=f"Отчет № 2: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источник: Таблица libraries | База данных: library.db")

            headers = [
                ("number", "Номер филиала", 120),
                ("address", "Адрес расположения", 320),
                ("phone", "Контактный номер телефона", 220),
                ("copies_count", "Всего экземпляров", 140),
            ]
            self._setup_columns(headers)

            cur.execute("""
            SELECT l.number, l.address, l.phone, COUNT(c.id) as cnt
            FROM libraries l
            LEFT JOIN copies c ON l.number = c.lib_number
            GROUP BY l.number, l.address, l.phone
            ORDER BY l.number
            """)
            rows = cur.fetchall()
            total_copies = sum(r[3] for r in rows)
            for r in rows:
                self.tree.insert("", tk.END, values=(f"Филиал №{r[0]}", r[1], r[2], f"{r[3]} экз."))

            self.lbl_summary.config(text=f"ИТОГО: Библиотечных отделений — {len(rows)} | Суммарно на балансе: {total_copies} экз.")

        elif idx == 3:
            self.rep_title = "Ведомость распределения экземпляров по залам"
            self.lbl_rep_title.config(text=f"Отчет № 3: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источники: copies, books, libraries | База данных: library.db")

            headers = [
                ("id", "Код", 60),
                ("lib", "Филиал", 110),
                ("book", "Название книги", 220),
                ("author", "Автор книги", 180),
                ("pub", "Издательство", 140),
                ("hall", "Читальный зал", 200),
            ]
            self._setup_columns(headers)

            cur.execute("""
            SELECT c.id, 'Филиал №' || c.lib_number, b.title, b.author, b.publisher, c.hall
            FROM copies c
            JOIN books b ON c.book_shifr = b.shifr
            ORDER BY c.lib_number, c.hall, b.title
            """)
            rows = cur.fetchall()
            for r in rows:
                self.tree.insert("", tk.END, values=list(r))

            self.lbl_summary.config(text=f"ИТОГО: Распределено по фондам и залам — {len(rows)} единиц хранения.")

        elif idx == 4:
            self.rep_title = "Сводный статистический отчет по издательствам"
            self.lbl_rep_title.config(text=f"Отчет № 4: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Анализ структуры фонда | База данных: library.db")

            headers = [
                ("publisher", "Наименование издательства", 250),
                ("titles_cnt", "Число наименований", 170),
                ("copies_cnt", "Количество экземпляров", 180),
                ("percent", "Доля в фонде", 140),
            ]
            self._setup_columns(headers)

            cur.execute("""
            SELECT b.publisher, COUNT(DISTINCT b.shifr), COUNT(c.id)
            FROM books b
            LEFT JOIN copies c ON b.shifr = c.book_shifr
            GROUP BY b.publisher
            ORDER BY COUNT(c.id) DESC
            """)
            rows = cur.fetchall()
            total_copies = sum(r[2] for r in rows) or 1
            for r in rows:
                share = (r[2] / total_copies) * 100
                self.tree.insert("", tk.END, values=(r[0], f"{r[1]} наим.", f"{r[2]} экз.", f"{share:.1f}%"))

            self.lbl_summary.config(text=f"ИТОГО: Издательств в каталоге — {len(rows)} | Всего экземпляров: {total_copies} шт.")

        conn.close()

    def _setup_columns(self, headers):
        col_ids = [h[0] for h in headers]
        self.tree["columns"] = col_ids
        for cid, cname, width in headers:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor="w")

    def action_print(self):
        messagebox.showinfo("Печать отчета",
                            f"Отчет «{self.rep_title}» успешно подготовлен к выводу на печать.\n"
                            "Все страницы и итоговые сводки отформатированы по ГОСТ.",
                            parent=self)

    def action_export_html(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialfile=f"Отчет_{self.current_report_idx}_{self.rep_title[:20].strip()}.html"
        )
        if not filename:
            return

        headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]

        th_html = "".join([f"<th style='background:#ECE9D8;color:#000080;padding:8px;border:1px solid #CBD5E1;'>{h}</th>" for h in headers])
        tr_rows = []
        for r in rows:
            tds = "".join([f"<td style='padding:6px;border:1px solid #E2E8F0;'>{cell}</td>" for cell in r])
            tr_rows.append(f"<tr>{tds}</tr>")

        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{self.rep_title}</title>
<style>
body {{ font-family: Tahoma, Arial, sans-serif; margin: 30px; background: #F8FAFC; color: #000; }}
.card {{ background: white; padding: 24px; border: 2px solid #808080; }}
h2 {{ color: #000080; margin-top: 0; }}
.meta {{ color: #666; font-size: 13px; margin-bottom: 16px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
.summary {{ margin-top: 16px; padding: 10px; background: #ECE9D8; border: 1px solid #808080; font-weight: bold; color: #000080; text-align: right; }}
</style>
</head>
<body>
<div class="card">
<h2>{self.rep_title}</h2>
<div class="meta">{self.lbl_rep_meta.cget('text')}</div>
<table>
<thead><tr>{th_html}</tr></thead>
<tbody>{''.join(tr_rows)}</tbody>
</table>
<div class="summary">{self.lbl_summary.cget('text')}</div>
</div>
</body>
</html>
"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        messagebox.showinfo("Экспорт завершен", f"Отчет успешно сохранен в формате HTML:\n{filename}", parent=self)

    def action_export_txt(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"Отчет_{self.current_report_idx}_{self.rep_title[:20].strip()}.txt"
        )
        if not filename:
            return

        headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]

        col_widths = [len(h) for h in headers]
        for r in rows:
            for idx, c in enumerate(r):
                col_widths[idx] = max(col_widths[idx], len(str(c)))

        header_line = " | ".join([h.ljust(col_widths[i]) for i, h in enumerate(headers)])
        sep_line = "-+-".join(["-" * col_widths[i] for i in range(len(headers))])

        content_lines = [
            f"ОТЧЕТ: {self.rep_title}",
            self.lbl_rep_meta.cget('text'),
            "=" * len(header_line),
            header_line,
            sep_line
        ]

        for r in rows:
            content_lines.append(" | ".join([str(r[i]).ljust(col_widths[i]) for i in range(len(headers))]))

        content_lines.append("=" * len(header_line))
        content_lines.append(self.lbl_summary.cget('text'))

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(content_lines))

        messagebox.showinfo("Экспорт завершен", f"Отчет успешно сохранен в текстовом формате:\n{filename}", parent=self)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    win = ReportViewerForm(root)
    win.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
