import os
import sys
import time
import ctypes
from ctypes import wintypes
import struct
import tkinter as tk
from PIL import Image

BASE_DIR = r"D:\study\projects\third\pbz\pbz6\pbz6_16"
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import init_db
from main import ModernMainWindow16
from forms import BooksForm16, LoansForm16
from table_view import TableViewForm16
from reports import ReportViewerForm16

IMG_DIR = os.path.join(BASE_DIR, "report_images")
os.makedirs(IMG_DIR, exist_ok=True)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def capture_widget_window(widget):
    widget.deiconify()
    widget.lift()
    widget.update_idletasks()
    widget.update()
    time.sleep(0.35)
    
    hwnd = widget.winfo_id()
    top_hwnd = user32.GetAncestor(hwnd, 2)
    target_hwnd = top_hwnd if top_hwnd else hwnd
    
    rect = wintypes.RECT()
    user32.GetWindowRect(target_hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    
    if w <= 0 or h <= 0:
        return None
        
    hwnd_dc = user32.GetWindowDC(target_hwnd)
    m_dc = gdi32.CreateCompatibleDC(hwnd_dc)
    bmp = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
    gdi32.SelectObject(m_dc, bmp)
    
    res = user32.PrintWindow(target_hwnd, m_dc, 2)
    if not res:
        res = user32.PrintWindow(target_hwnd, m_dc, 0)
        
    bmi = bytearray(40)
    struct.pack_into('<IiiHHIIIIII', bmi, 0, 40, w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
    buf = bytearray(w * h * 4)
    gdi32.GetDIBits(m_dc, bmp, 0, h, (ctypes.c_char * len(buf)).from_buffer(buf), (ctypes.c_char * 40).from_buffer(bmi), 0)
    
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(m_dc)
    user32.ReleaseDC(target_hwnd, hwnd_dc)
    
    img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1).convert('RGB')
    return img

def main():
    print("Инициализация базы данных и захват скриншотов для Варианта 16 (ЛР 6)...")
    init_db()
    
    app = ModernMainWindow16()
    app.update()
    
    # 1. Главное окно
    img_main = capture_widget_window(app)
    img_main.save(os.path.join(IMG_DIR, "win_main.png"))
    print("1/8 Главное окно сохранено:", img_main.size)
    
    # 2. Форма ввода с кнопками «Таблица» и «Отчёт»
    f_loans = LoansForm16(app)
    f_loans.update()
    img_loans = capture_widget_window(f_loans)
    img_loans.save(os.path.join(IMG_DIR, "win_record_form.png"))
    print("2/8 Форма ввода с кнопками сохранена:", img_loans.size)
    f_loans.destroy()
    app.update()
    
    # 3. Табличная форма с блоком сортировки и фильтрации
    f_tbl = TableViewForm16(app, initial_table="books")
    f_tbl.update()
    img_tbl = capture_widget_window(f_tbl)
    img_tbl.save(os.path.join(IMG_DIR, "win_table_view.png"))
    print("3/8 Табличная форма сохранена:", img_tbl.size)
    
    # 4. Результат поиска с выделением строк
    f_tbl.search_var.set("Оруэлл")
    f_tbl.apply_search()
    f_tbl.update()
    img_search = capture_widget_window(f_tbl)
    img_search.save(os.path.join(IMG_DIR, "win_table_search.png"))
    print("4/8 Результат поиска сохранен:", img_search.size)
    f_tbl.destroy()
    app.update()
    
    # 5. Отчет 1: Каталог книжного фонда
    f_rep1 = ReportViewerForm16(app, default_report_index=1)
    f_rep1.update()
    img_r1 = capture_widget_window(f_rep1)
    img_r1.save(os.path.join(IMG_DIR, "win_report1.png"))
    print("5/8 Отчет 1 сохранен:", img_r1.size)
    f_rep1.destroy()
    app.update()
    
    # 6. Отчет 2: Картотека читателей
    f_rep2 = ReportViewerForm16(app, default_report_index=2)
    f_rep2.update()
    img_r2 = capture_widget_window(f_rep2)
    img_r2.save(os.path.join(IMG_DIR, "win_report2.png"))
    print("6/8 Отчет 2 сохранен:", img_r2.size)
    f_rep2.destroy()
    app.update()
    
    # 7. Отчет 3: Журнал учета выдачи книг
    f_rep3 = ReportViewerForm16(app, default_report_index=3)
    f_rep3.update()
    img_r3 = capture_widget_window(f_rep3)
    img_r3.save(os.path.join(IMG_DIR, "win_report3.png"))
    print("7/8 Отчет 3 сохранен:", img_r3.size)
    f_rep3.destroy()
    app.update()
    
    # 8. Отчет 4: Ведомость сроков возврата
    f_rep4 = ReportViewerForm16(app, default_report_index=4)
    f_rep4.update()
    img_r4 = capture_widget_window(f_rep4)
    img_r4.save(os.path.join(IMG_DIR, "win_report4.png"))
    print("8/8 Отчет 4 сохранен:", img_r4.size)
    f_rep4.destroy()
    app.update()
    
    app.destroy()
    print("Все 8 скриншотов успешно созданы в:", IMG_DIR)

if __name__ == "__main__":
    main()
