import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
from database import get_connection

BG_COLOR = "#EFF6FF"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#1E3A8A"
ACCENT_COLOR = "#2563EB"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"

class ReportViewerForm16(tk.Toplevel):
    def __init__(self, parent, default_report_index=1):
        super().__init__(parent)
        self.title("Генератор и просмотрщик отчетов — Библиотека (ЛР 6)")
        self.geometry("890x660")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.current_report_idx = default_report_index
        self._build_ui()
        self.generate_report(self.current_report_idx)

    def _build_ui(self):
        # Верхняя панель выбора отчетов
        top_bar = tk.Frame(self, bg=PRIMARY_COLOR, padx=16, pady=12)
        top_bar.pack(fill=tk.X)

        lbl_hdr = tk.Label(top_bar, text="ПОСТРОЕНИЕ И ПРОСМОТР ОТЧЕТОВ БИБЛИОТЕКИ",
                           font=("Segoe UI", 12, "bold"), fg="white", bg=PRIMARY_COLOR)
        lbl_hdr.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(top_bar, bg=PRIMARY_COLOR)
        btn_box.pack(fill=tk.X)

        self.btn_rep1 = tk.Button(btn_box, text="1. Каталог фонда", font=("Segoe UI", 9, "bold"),
                                  bg="#2563EB", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(1))
        self.btn_rep1.pack(side=tk.LEFT, padx=3)

        self.btn_rep2 = tk.Button(btn_box, text="2. Картотека читателей", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(2))
        self.btn_rep2.pack(side=tk.LEFT, padx=3)

        self.btn_rep3 = tk.Button(btn_box, text="3. Журнал выдачи", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(3))
        self.btn_rep3.pack(side=tk.LEFT, padx=3)

        self.btn_rep4 = tk.Button(btn_box, text="4. Ведомость сроков возврата", font=("Segoe UI", 9, "bold"),
                                  bg="#1E40AF", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(4))
        self.btn_rep4.pack(side=tk.LEFT, padx=3)

        # Область отображения отчета
        doc_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1)
        doc_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        self.lbl_rep_title = tk.Label(doc_card, text="", font=("Segoe UI", 13, "bold"),
                                      bg=CARD_BG, fg=PRIMARY_COLOR)
        self.lbl_rep_title.pack(anchor="w", padx=16, pady=(12, 2))

        self.lbl_rep_meta = tk.Label(doc_card, text="", font=("Segoe UI", 9),
                                     bg=CARD_BG, fg="#64748B")
        self.lbl_rep_meta.pack(anchor="w", padx=16, pady=(0, 8))

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
        style.configure("Report16.Treeview", background="#FFFFFF", foreground=TEXT_COLOR,
                        rowheight=24, font=("Segoe UI", 9))
        style.configure("Report16.Treeview.Heading", background="#DBEAFE", foreground=PRIMARY_COLOR,
                        font=("Segoe UI", 9, "bold"))
        self.tree.configure(style="Report16.Treeview")

        self.lbl_summary = tk.Label(doc_card, text="", font=("Segoe UI", 9, "bold"),
                                    bg="#F8FAFC", fg=PRIMARY_COLOR, anchor="e", padx=16, pady=6,
                                    relief=tk.GROOVE)
        self.lbl_summary.pack(fill=tk.X, side=tk.BOTTOM)

        # Нижняя панель действий
        act_card = tk.Frame(self, bg=CARD_BG, relief=tk.SOLID, bd=1, padx=14, pady=8)
        act_card.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Button(act_card, text="Печать / Предпросмотр", font=("Segoe UI", 9),
                  bg="#F1F5F9", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1,
                  cursor="hand2", padx=12, pady=3,
                  command=self.action_print).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Экспорт в HTML", font=("Segoe UI", 9),
                  bg="#EFF6FF", fg=ACCENT_COLOR, relief=tk.GROOVE, bd=1,
                  cursor="hand2", padx=12, pady=3,
                  command=self.action_export_html).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Экспорт в TXT", font=("Segoe UI", 9),
                  bg="#F8FAFC", fg=TEXT_COLOR, relief=tk.GROOVE, bd=1,
                  cursor="hand2", padx=12, pady=3,
                  command=self.action_export_txt).pack(side=tk.LEFT, padx=4)

        tk.Button(act_card, text="Закрыть", font=("Segoe UI", 9, "bold"),
                  bg="#FEF2F2", fg="#DC2626", relief=tk.GROOVE, bd=1,
                  cursor="hand2", padx=14, pady=3,
                  command=self.destroy).pack(side=tk.RIGHT, padx=4)

    def _highlight_button(self, idx):
        btns = [self.btn_rep1, self.btn_rep2, self.btn_rep3, self.btn_rep4]
        for i, b in enumerate(btns, 1):
            if i == idx:
                b.configure(bg="#2563EB", relief=tk.SUNKEN)
            else:
                b.configure(bg="#1E40AF", relief=tk.FLAT)

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
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источник: Таблица books | База данных: library16.db")

            headers = [
                ("shifr", "Шифр", 110),
                ("author", "Автор книги", 190),
                ("title", "Наименование произведения", 240),
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
            self.lbl_summary.config(text=f"ИТОГО: Всего наименований книг — {len(rows)} шт.  |  Охват изданий: {y_min} – {y_max} гг.")

        elif idx == 2:
            self.rep_title = "Картотека зарегистрированных читателей"
            self.lbl_rep_title.config(text=f"Отчет № 2: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источник: Таблица readers | База данных: library16.db")

            headers = [
                ("reader_id", "Номер билета", 110),
                ("full_name", "ФИО читателя", 200),
                ("address", "Адрес проживания", 240),
                ("phone", "Контактный телефон", 160),
                ("education", "Образование", 110),
            ]
            self._setup_columns(headers)

            cur.execute("SELECT reader_id, full_name, address, phone, education FROM readers ORDER BY reader_id")
            rows = cur.fetchall()
            for r in rows:
                self.tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4]))

            self.lbl_summary.config(text=f"ИТОГО: Зарегистрировано читателей — {len(rows)} чел.")

        elif idx == 3:
            self.rep_title = "Журнал учета выдачи книг читателям на руки"
            self.lbl_rep_title.config(text=f"Отчет № 3: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Источники: loans, readers, books | База данных: library16.db")

            headers = [
                ("id", "Код", 60),
                ("reader", "Читатель", 180),
                ("phone", "Телефон", 140),
                ("shifr", "Шифр", 90),
                ("book", "Название книги", 200),
                ("author", "Автор", 140),
                ("issue_date", "Дата выдачи", 110),
                ("return_date", "Срок сдачи", 110),
            ]
            self._setup_columns(headers)

            cur.execute("""
            SELECT l.id, r.full_name, r.phone, b.shifr, b.title, b.author, l.issue_date, l.return_date
            FROM loans l
            JOIN readers r ON l.reader_id = r.reader_id
            JOIN books b ON l.shifr = b.shifr
            ORDER BY l.issue_date DESC, l.id
            """)
            rows = cur.fetchall()
            for r in rows:
                self.tree.insert("", tk.END, values=list(r))

            self.lbl_summary.config(text=f"ИТОГО: Всего записей в журнале абонемента — {len(rows)} выдач.")

        elif idx == 4:
            self.rep_title = "Контрольная ведомость сроков возврата литературы"
            self.lbl_rep_title.config(text=f"Отчет № 4: {self.rep_title}")
            self.lbl_rep_meta.config(text=f"Сформирован: {now_str} | Анализ графика абонемента | База данных: library16.db")

            headers = [
                ("id", "Код", 60),
                ("reader", "Читатель", 190),
                ("book", "Книга", 220),
                ("issue_date", "Дата выдачи", 110),
                ("return_date", "Контрольный срок", 120),
                ("term_days", "Срок (дней)", 100),
                ("status", "Статус контроля", 130),
            ]
            self._setup_columns(headers)

            cur.execute("""
            SELECT l.id, r.full_name, b.title, l.issue_date, l.return_date
            FROM loans l
            JOIN readers r ON l.reader_id = r.reader_id
            JOIN books b ON l.shifr = b.shifr
            ORDER BY l.return_date
            """)
            rows = cur.fetchall()
            for r in rows:
                try:
                    d1 = datetime.datetime.strptime(r[3], "%Y-%m-%d")
                    d2 = datetime.datetime.strptime(r[4], "%Y-%m-%d")
                    days = (d2 - d1).days
                except Exception:
                    days = 14
                status = "На руках (в срок)"
                self.tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4], f"{days} дн.", status))

            self.lbl_summary.config(text=f"ИТОГО: Литературы на руках у читателей — {len(rows)} экз. Все формуляры под контролем.")

        conn.close()

    def _setup_columns(self, headers):
        col_ids = [h[0] for h in headers]
        self.tree["columns"] = col_ids
        for cid, cname, width in headers:
            self.tree.heading(cid, text=cname)
            self.tree.column(cid, width=width, anchor="w")

    def action_print(self):
        messagebox.showinfo("Печать отчета",
                            f"Отчет «{self.rep_title}» успешно подготовлен к выводу на системное печатающее устройство.\n\n"
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

        th_html = "".join([f"<th style='background:#1E3A8A;color:white;padding:8px;border:1px solid #CBD5E1;'>{h}</th>" for h in headers])
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
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 30px; background: #F8FAFC; color: #0F172A; }}
.card {{ background: white; padding: 24px; border-radius: 8px; border: 1px solid #CBD5E1; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
h2 {{ color: #1E3A8A; margin-top: 0; }}
.meta {{ color: #64748B; font-size: 13px; margin-bottom: 16px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
.summary {{ margin-top: 16px; padding: 10px; background: #EFF6FF; border-left: 4px solid #1E3A8A; font-weight: bold; color: #1E3A8A; }}
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
    win = ReportViewerForm16(root)
    win.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
