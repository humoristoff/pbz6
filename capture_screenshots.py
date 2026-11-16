import os
import sys
import time
import ctypes
from ctypes import wintypes
import struct
import tkinter as tk
from PIL import Image

BASE_DIR = r"D:\study\projects\third\pbz\pbz6"
os.chdir(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database import init_db
from main import MainWindow
from forms import BooksForm, CopiesForm
from table_view import TableViewForm
from reports import ReportViewerForm

IMG_DIR = os.path.join(BASE_DIR, "report_images")
os.makedirs(IMG_DIR, exist_ok=True)

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

def capture_widget_window(widget):
    widget.deiconify()
    widget.lift()
    widget.update_idletasks()
    widget.update()
    time.sleep(0.3)
    
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
    print("Инициализация базы данных и захват скриншотов для Варианта 17 (ЛР 6)...")
    init_db()
    
    app = MainWindow()
    app.update()
    
    # 1. Главное окно
    img_main = capture_widget_window(app)
    img_main.save(os.path.join(IMG_DIR, "win_main.png"))
    print("1/8 Главное окно сохранено:", img_main.size)
    
    # 2. Ленточная форма с навигатором, кнопками 'Таблица' и 'Отчёт'
    f_books = BooksForm(app)
    f_books.update()
    img_books = capture_widget_window(f_books)
    img_books.save(os.path.join(IMG_DIR, "win_record_form.png"))
    print("2/8 Ленточная форма сохранена:", img_books.size)
    f_books.destroy()
    app.update()
    
    # 3. Табличная форма с блоком сортировки, фильтром и поиском (Рис. 11.10)
    f_tbl = TableViewForm(app, initial_table="books")
    f_tbl.update()
    img_tbl = capture_widget_window(f_tbl)
    img_tbl.save(os.path.join(IMG_DIR, "win_table_view.png"))
    print("3/8 Табличная форма сохранена:", img_tbl.size)

    # 4. Демонстрация поиска и подсветки ячеек
    f_tbl.search_var.set("АСТ")
    f_tbl.apply_search()
    f_tbl.update()
    img_search = capture_widget_window(f_tbl)
    img_search.save(os.path.join(IMG_DIR, "win_table_search.png"))
    print("4/8 Результат поиска сохранен:", img_search.size)
    f_tbl.destroy()
    app.update()

    # 5. Отчет 1: Каталог фонда
    f_rep = ReportViewerForm(app, default_report_index=1)
    f_rep.update()
    img_rep1 = capture_widget_window(f_rep)
    img_rep1.save(os.path.join(IMG_DIR, "win_report1.png"))
    print("5/8 Отчет 1 сохранен:", img_rep1.size)

    # 6. Отчет 2: Филиалы
    f_rep.generate_report(2)
    f_rep.update()
    img_rep2 = capture_widget_window(f_rep)
    img_rep2.save(os.path.join(IMG_DIR, "win_report2.png"))
    print("6/8 Отчет 2 сохранен:", img_rep2.size)

    # 7. Отчет 3: Экземпляры
    f_rep.generate_report(3)
    f_rep.update()
    img_rep3 = capture_widget_window(f_rep)
    img_rep3.save(os.path.join(IMG_DIR, "win_report3.png"))
    print("7/8 Отчет 3 сохранен:", img_rep3.size)

    # 8. Отчет 4: Сводный по издательствам
    f_rep.generate_report(4)
    f_rep.update()
    img_rep4 = capture_widget_window(f_rep)
    img_rep4.save(os.path.join(IMG_DIR, "win_report4.png"))
    print("8/8 Отчет 4 сохранен:", img_rep4.size)
    f_rep.destroy()
    
    app.destroy()
    print("Все скриншоты успешно сгенерированы в", IMG_DIR)

if __name__ == "__main__":
    main()
