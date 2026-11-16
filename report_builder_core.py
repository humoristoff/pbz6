import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

TEMPLATE_PATH = r"D:\Downloads\Telegram Desktop\Корнелюк лаб5 (1).docx"
if not os.path.exists(TEMPLATE_PATH):
    TEMPLATE_PATH = r"C:\Users\RUSLAN\.gemini\antigravity\brain\192683ef-9f92-480a-b54c-c4a14e3b0521\.user_uploaded\media_1794829585925_01bf108f.docx"

OUT_DIR = r"D:\study\отчеты лаб\пбз"
os.makedirs(OUT_DIR, exist_ok=True)

def add_empty_line(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run("")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p

def add_text_para(doc, text, bold=False, indent_spaces=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if indent_spaces > 0:
        r_indent = p.add_run(" " * indent_spaces)
        r_indent.font.name = "Times New Roman"
        r_indent.font.size = Pt(12)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = bold
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_goal_para(doc, goal_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    
    r_sp = p.add_run("         ")
    r_sp.font.name = "Times New Roman"
    r_sp.font.size = Pt(12)

    r_bold = p.add_run("Цель")
    r_bold.font.name = "Times New Roman"
    r_bold.font.size = Pt(12)
    r_bold.bold = True
    r_bold.font.color.rgb = RGBColor(0, 0, 0)

    r_txt = p.add_run(f": {goal_text}")
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(12)
    r_txt.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_code_header(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_code_line(doc, line_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(line_text if line_text else "")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p

def add_screenshot_item(doc, label, img_path, width_in=5.8):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(label)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.bold = True
    r.font.color.rgb = RGBColor(0, 0, 0)

    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.line_spacing = 1.0
        r_img = p_img.add_run()
        r_img.add_picture(img_path, width=Inches(width_in))
    add_empty_line(doc)

def add_conclusion_item(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    
    r_bold = p.add_run("Вывод")
    r_bold.font.name = "Times New Roman"
    r_bold.font.size = Pt(12)
    r_bold.bold = True
    r_bold.font.color.rgb = RGBColor(0, 0, 0)

    r_rest = p.add_run(f": {text}")
    r_rest.font.name = "Times New Roman"
    r_rest.font.size = Pt(12)
    r_rest.font.color.rgb = RGBColor(0, 0, 0)

def set_cell_border(cell, color="A0AEC0", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'  <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def add_struct_table(doc, title_text, rows_data):
    add_text_para(doc, title_text, bold=True)
    
    col_widths = [Inches(1.2), Inches(1.5), Inches(2.6), Inches(1.9)]
    t = doc.add_table(rows=1, cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr = t.rows[0].cells
    hdr_titles = ["Поле", "Тип", "Ограничение / ключ", "Назначение"]
    for i, htitle in enumerate(hdr_titles):
        hdr[i].text = htitle
        hdr[i].width = col_widths[i]
        set_cell_border(hdr[i], color="243854", sz="6")
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="243854"/>')
        hdr[i]._tc.get_or_add_tcPr().append(shd)
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.0
        r = p.runs[0]
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for row_idx, row_values in enumerate(rows_data):
        row = t.add_row().cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for i, val in enumerate(row_values):
            row[i].text = val
            row[i].width = col_widths[i]
            set_cell_border(row[i], color="CBD5E1", sz="4")
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
            row[i]._tc.get_or_add_tcPr().append(shd)
            p = row[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            r = p.runs[0]
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(0, 0, 0)
            if i == 0:
                r.bold = True
                
    add_empty_line(doc)

def set_title_page(doc, lab_num_str, topic_str, variant_num, student_line1, student_line2, student_name):
    # p9: ЛАБОРАТОРНАЯ РАБОТА №6
    p9 = doc.paragraphs[9]
    for r in p9.runs:
        r.text = ""
    r9 = p9.add_run(lab_num_str)
    r9.font.name = "Times New Roman"
    r9.font.size = Pt(16)
    r9.bold = True

    # p10: дисциплина
    p10 = doc.paragraphs[10]
    for r in p10.runs:
        r.text = ""
    r10 = p10.add_run("По дисциплине «Проектирование баз знаний» за 5 семестр")
    r10.font.name = "Times New Roman"
    r10.font.size = Pt(14)

    # p11: тема
    p11 = doc.paragraphs[11]
    for r in p11.runs:
        r.text = ""
    r11 = p11.add_run(topic_str)
    r11.font.name = "Times New Roman"
    r11.font.size = Pt(14)

    # p12: вариант
    p12 = doc.paragraphs[12]
    for r in p12.runs:
        r.text = ""
    r12 = p12.add_run(f"Вариант {variant_num}")
    r12.font.name = "Times New Roman"
    r12.font.size = Pt(14)

    # p20: Выполнил
    p20 = doc.paragraphs[20]
    for r in p20.runs:
        r.text = ""
    r20 = p20.add_run(student_line1)
    r20.font.name = "Times New Roman"
    r20.font.size = Pt(14)

    # p21: Студент 3 курса
    p21 = doc.paragraphs[21]
    for r in p21.runs:
        r.text = ""
    r21 = p21.add_run(student_line2)
    r21.font.name = "Times New Roman"
    r21.font.size = Pt(14)

    # p22: группы ИИ-28
    p22 = doc.paragraphs[22]
    for r in p22.runs:
        r.text = ""
    r22 = p22.add_run("группы ИИ-28")
    r22.font.name = "Times New Roman"
    r22.font.size = Pt(14)

    # p23: (2 подгруппа)
    p23 = doc.paragraphs[23]
    for r in p23.runs:
        r.text = ""
    r23 = p23.add_run("(2 подгруппа)")
    r23.font.name = "Times New Roman"
    r23.font.size = Pt(14)

    # p24: ФИО
    p24 = doc.paragraphs[24]
    for r in p24.runs:
        r.text = ""
    r24 = p24.add_run(student_name)
    r24.font.name = "Times New Roman"
    r24.font.size = Pt(14)

    # p25: Проверил:
    p25 = doc.paragraphs[25]
    for r in p25.runs:
        r.text = ""
    r25 = p25.add_run("Проверил:")
    r25.font.name = "Times New Roman"
    r25.font.size = Pt(14)

    # p26: Савонюк В. А.
    p26 = doc.paragraphs[26]
    for r in p26.runs:
        r.text = ""
    r26 = p26.add_run("Савонюк В. А.  ")
    r26.font.name = "Times New Roman"
    r26.font.size = Pt(14)

    # p32: Брест 2026
    p32 = doc.paragraphs[32]
    for r in p32.runs:
        r.text = ""
    r32 = p32.add_run("Брест 2026")
    r32.font.name = "Times New Roman"
    r32.font.size = Pt(14)

    # Удаление старых параграфов 33..end
    all_paras = list(doc.paragraphs)
    for p in all_paras[33:]:
        p._p.getparent().remove(p._p)

def append_common_lab6_intro(doc, variant_desc, tables_meta):
    add_empty_line(doc)
    add_goal_para(doc, "получить навыки разработки приложений БД и организации пользовательского интерфейса: табличного представления информации и построения отчетов.")
    add_empty_line(doc)

    add_text_para(doc, "Задание.")
    add_text_para(doc, "1. Изучить теоретический материал по организации табличного представления информации и построения аналитических отчетов в приложениях баз данных.")
    add_text_para(doc, "2. На основании логической модели данных предметной области (в соответствии с вариантом) спроектировать и реализовать:")
    add_text_para(doc, "    – табличную форму отображения данных с настраиваемой сортировкой записей по выбранным полям (по возрастанию / по убыванию);", indent_spaces=3)
    add_text_para(doc, "    – панель фильтрации с выпадающим списком уникальных значений и возможностью сброса фильтра («Показать все»);", indent_spaces=3)
    add_text_para(doc, "    – панель контекстного поиска записей по произвольным критериям с визуальным выделением (подсветкой) найденных строк;", indent_spaces=3)
    add_text_para(doc, "    – элементы навигации и быстрого перехода к табличному представлению («Таблица») и отчетам («Отчёт») непосредственно из экранных форм ввода записей;", indent_spaces=3)
    add_text_para(doc, "    – не менее 4 специализированных аналитических отчетов по предметной области с расчетом итоговых показателей, поддержкой предварительного просмотра и экспорта данных.", indent_spaces=3)
    add_empty_line(doc)

    add_text_para(doc, variant_desc)
    add_empty_line(doc)

    add_text_para(doc, "1.2. Структура таблиц", bold=True)
    add_text_para(doc, "В базе данных три таблицы. Ниже перечислены их поля, типы, ограничения и назначение.")
    add_empty_line(doc)

    for tbl_title, rows in tables_meta:
        add_struct_table(doc, tbl_title, rows)

def append_code_modules(doc, code_files):
    add_text_para(doc, "Программный код созданного приложения:")
    add_empty_line(doc)

    for header_title, file_path in code_files:
        add_code_header(doc, header_title)
        add_empty_line(doc)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                add_code_line(doc, line.rstrip("\r\n"))
        else:
            add_code_line(doc, f"# Файл не найден: {file_path}")
        add_empty_line(doc)

def append_screenshots_and_conclusion(doc, screenshots, conclusion_text):
    add_code_header(doc, "Скриншоты:")
    add_empty_line(doc)

    for idx, (label, img_path) in enumerate(screenshots, 1):
        add_screenshot_item(doc, f"{idx}. {label}:", img_path)

    add_empty_line(doc)
    add_conclusion_item(doc, conclusion_text)

print("Helper definitions loaded successfully.")
