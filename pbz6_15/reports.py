import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import datetime
from database import get_connection

BG_COLOR = "#F0FDF4"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#0F766E"
ACCENT_COLOR = "#047857"
TEXT_COLOR = "#0F172A"
BORDER_COLOR = "#CBD5E1"

class ReportViewerForm15(tk.Toplevel):
    def __init__(self, parent, default_report_index=1):
        super().__init__(parent)
        self.title("Генератор и просмотрщик отчетов — Склад товаров (ЛР 6)")
        self.geometry("940x660")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.current_report_idx = default_report_index
        self._build_ui()
        self.generate_report(self.current_report_idx)

    def _build_ui(self):
        # 1. Верхняя панель выбора отчета (4 отчета)
        top_bar = tk.Frame(self, bg=PRIMARY_COLOR, padx=16, pady=12)
        top_bar.pack(fill=tk.X)

        lbl_hdr = tk.Label(top_bar, text="ПОСТРОЕНИЕ И ПРОСМОТР ОТЧЕТОВ СКЛАДСКОГО УЧЕТА",
                           font=("Segoe UI", 12, "bold"), fg="white", bg=PRIMARY_COLOR)
        lbl_hdr.pack(anchor="w", pady=(0, 6))

        btn_box = tk.Frame(top_bar, bg=PRIMARY_COLOR)
        btn_box.pack(fill=tk.X)

        self.btn_rep1 = tk.Button(btn_box, text="1. Остатки номенклатуры", font=("Segoe UI", 9, "bold"),
                                  bg="#0D9488", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(1))
        self.btn_rep1.pack(side=tk.LEFT, padx=3)

        self.btn_rep2 = tk.Button(btn_box, text="2. Склады и емкости", font=("Segoe UI", 9, "bold"),
                                  bg="#115E59", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(2))
        self.btn_rep2.pack(side=tk.LEFT, padx=3)

        self.btn_rep3 = tk.Button(btn_box, text="3. Реестр производителей", font=("Segoe UI", 9, "bold"),
                                  bg="#115E59", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(3))
        self.btn_rep3.pack(side=tk.LEFT, padx=3)

        self.btn_rep4 = tk.Button(btn_box, text="4. Инвентаризационная ведомость", font=("Segoe UI", 9, "bold"),
                                  bg="#115E59", fg="white", relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                                  command=lambda: self.generate_report(4))
        self.btn_rep4.pack(side=tk.LEFT, padx=3)

        # 2. Область отображения отчета
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
        style.configure("Report15.Treeview", background="#FFFFFF", foreground=TEXT_COLOR,
                        rowheight=24, font=("Segoe UI", 9))
        style.configure("Report15.Treeview.Heading", background="#CCFBF1", foreground=PRIMARY_COLOR,
                        font=("Segoe UI", 9, "bold"))
        self.tree.configure(style="Report15.Treeview")

        self.lbl_summary = tk.Label(doc_card, text="", font=("Segoe UI", 9, "bold"),
                                    bg="#F8FAFC", fg=PRIMARY_COLOR, anchor="e", padx=16, pady=6,
                                    relief=tk.GROOVE)
        self.lbl_summary.pack(fill=tk.X, side=tk.BOTTOM)

        # 3. Нижняя панель действий
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
                b.configure(bg="#0D9488", relief=tk.SUNKEN)
            else:
                b.configure(bg="#115E59", relief=tk.FLAT)

    def generate_report(self, report_idx):
        self.current_report_idx = report_idx
        self._update_button_styles(report_idx)

        for col in self.tree.get_children():
            self.tree.delete(col)

        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        conn = get_connection()
        cur = conn.cursor()

        if report_idx == 1:
            title = "ОТЧЕТ №1: Ведомость складских остатков и номенклатуры продукции"
            meta = f"Формирование отчета: {now_str} • Параметры: поэкземплярный учет остатков"
            cols = [("id", "Код", 50), ("name", "Товар", 180), ("sklad", "Склад / Фирма", 170),
                    ("adres", "Адрес склада", 160), ("proiz", "Производитель", 150),
                    ("ed", "Ед. изм.", 70), ("kol", "Остаток", 80)]
            cur.execute("""
            SELECT t.kod_tovara, t.name_t, s.firma, s.adres, p.name_proiz, t.edizmer, t.kol
            FROM tovary t
            JOIN sklady s ON t.kod_sklada = s.kod_sklada
            JOIN proizvoditeli p ON t.kod_proiz = p.kod_proiz
            ORDER BY t.kod_tovara
            """)
            rows = cur.fetchall()
            total_items = sum(r[6] for r in rows)
            summary = f"ИТОГО: {len(rows)} номенклатурных позиций | Всего единиц в наличии: {total_items}"

        elif report_idx == 2:
            title = "ОТЧЕТ №2: Справочник складских комплексов и емкостей хранения"
            meta = f"Формирование отчета: {now_str} • Параметры: сводка по логистическим центрам"
            cols = [("id", "Код", 60), ("firma", "Организация / Фирма", 220), ("adres", "Адрес", 240),
                    ("phone", "Телефон", 140), ("cnt", "Позиций", 90), ("total", "Суммарный объем", 120)]
            cur.execute("""
            SELECT s.kod_sklada, s.firma, s.adres, s.telefon, COUNT(t.kod_tovara), COALESCE(SUM(t.kol), 0)
            FROM sklady s
            LEFT JOIN tovary t ON s.kod_sklada = t.kod_sklada
            GROUP BY s.kod_sklada, s.firma, s.adres, s.telefon
            ORDER BY s.kod_sklada
            """)
            rows = cur.fetchall()
            tot_v = sum(r[5] for r in rows)
            summary = f"ИТОГО: {len(rows)} складов | Общий остаток по всем складам: {tot_v} ед."

        elif report_idx == 3:
            title = "ОТЧЕТ №3: Реестр заводов-производителей и стран происхождения"
            meta = f"Формирование отчета: {now_str} • Параметры: реестр поставщиков и охват товаров"
            cols = [("id", "Код", 60), ("name", "Производитель", 210), ("strana", "Страна", 120),
                    ("adres", "Адрес завода", 240), ("phone", "Телефон", 140), ("t_cnt", "Товаров", 90)]
            cur.execute("""
            SELECT p.kod_proiz, p.name_proiz, p.strana, p.adres_proiz, p.telefon_proiz, COUNT(t.kod_tovara)
            FROM proizvoditeli p
            LEFT JOIN tovary t ON p.kod_proiz = t.kod_proiz
            GROUP BY p.kod_proiz, p.name_proiz, p.strana, p.adres_proiz, p.telefon_proiz
            ORDER BY p.kod_proiz
            """)
            rows = cur.fetchall()
            summary = f"ИТОГО: {len(rows)} производителей в реестре"

        elif report_idx == 4:
            title = "ОТЧЕТ №4: Сводная инвентаризационная ведомость по складам"
            meta = f"Формирование отчета: {now_str} • Параметры: группировка остатков по складам"
            cols = [("sklad_id", "Код склада", 90), ("firma", "Склад / Владелец", 260),
                    ("positions", "Число наименований", 180), ("total_qty", "Общее число единиц", 180),
                    ("share", "Доля от общего фонда", 150)]
            cur.execute("""
            SELECT s.kod_sklada, s.firma, COUNT(t.kod_tovara), COALESCE(SUM(t.kol), 0)
            FROM sklady s
            LEFT JOIN tovary t ON s.kod_sklada = t.kod_sklada
            GROUP BY s.kod_sklada, s.firma
            ORDER BY SUM(t.kol) DESC
            """)
            raw = cur.fetchall()
            grand_total = sum(r[3] for r in raw) or 1
            rows = []
            for r in raw:
                pct = f"{(r[3] / grand_total) * 100:.1f} %"
                rows.append((r[0], r[1], r[2], r[3], pct))
            summary = f"ИТОГО ПО ИНВЕНТАРИЗАЦИИ: {grand_total} единиц продукции"

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
               f"Документ готов к печати.")
        messagebox.showinfo("Печать отчета", msg, parent=self)

    def export_html(self):
        fpath = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".html",
            filetypes=[("HTML файлы", "*.html"), ("Все файлы", "*.*")],
            initialfile=f"склад_отчет_{self.current_report_idx}.html"
        )
        if not fpath:
            return

        headers_html = "".join([f"<th style='border:1px solid #CBD5E1; padding:8px; background:#0F766E; color:white;'>{c[1]}</th>" for c in self.current_cols])
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
        h2 {{ color: #0F766E; margin-bottom: 4px; }}
        .meta {{ color: #64748B; font-size: 13px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
        .summary {{ margin-top: 20px; font-weight: bold; color: #0F766E; }}
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
            initialfile=f"склад_отчет_{self.current_report_idx}.txt"
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
