import os
import sys
import docx
from report_builder_core import (
    TEMPLATE_PATH, OUT_DIR, set_title_page, append_common_lab6_intro,
    append_code_modules, append_screenshots_and_conclusion
)

TOPIC = "Тема: «Создание приложения для работы с БД организация пользовательского интерфейса: табличное представление и отчеты»"
LAB_TITLE = "ЛАБОРАТОРНАЯ РАБОТА №6"

def build_v17():
    out_path = os.path.join(OUT_DIR, "ЛР 6 ПБЗ.docx")
    print(f"Генерация {out_path} (Вариант 17 - Манцевич Р.С.)...")
    doc = docx.Document(TEMPLATE_PATH)

    set_title_page(
        doc,
        lab_num_str=LAB_TITLE,
        topic_str=TOPIC,
        variant_num=17,
        student_line1="Выполнил:",
        student_line2="Студент 3 курса",
        student_name="Манцевич Р.С."
    )

    variant_desc = "Вариант 17: база данных, содержащая таблицы BOOKS (Книги), LIBRARIES (Библиотеки) и COPIES (Экземпляры)."
    tables_meta = [
        ("Таблица BOOKS — каталог книжного фонда библиотечной сети.", [
            ("shifr", "TEXT NOT NULL", "PK_Books (первичный ключ)", "Каталожный шифр книги (напр. B001)"),
            ("author", "TEXT NOT NULL", "—", "Фамилия и инициалы автора книги"),
            ("title", "TEXT NOT NULL", "—", "Наименование литературного произведения"),
            ("publisher", "TEXT NOT NULL", "—", "Издательство"),
            ("year", "INTEGER NOT NULL", "CK_Books_Year (year > 0)", "Год публикации книги"),
        ]),
        ("Таблица LIBRARIES — реестр филиалов и библиотек сети.", [
            ("number", "INTEGER NOT NULL", "PK_Libraries (первичный ключ)", "Номер филиала библиотеки"),
            ("address", "TEXT NOT NULL", "—", "Фактический адрес филиала"),
            ("phone", "TEXT NOT NULL", "—", "Контактный номер телефона"),
        ]),
        ("Таблица COPIES — распределение экземпляров книг по библиотекам и залам.", [
            ("id", "INTEGER NOT NULL", "PK_Copies (AUTOINCREMENT)", "Суррогатный первичный ключ экземпляра"),
            ("lib_number", "INTEGER NOT NULL", "FK_Copies_Libraries -> libraries(number) ON UPDATE CASCADE ON DELETE CASCADE", "Номер филиала библиотеки"),
            ("book_shifr", "TEXT NOT NULL", "FK_Copies_Books -> books(shifr) ON UPDATE CASCADE ON DELETE CASCADE", "Шифр книги"),
            ("hall", "TEXT NOT NULL", "—", "Наименование читального зала библиотеки"),
        ]),
    ]
    append_common_lab6_intro(doc, variant_desc, tables_meta)

    base_proj = r"D:\study\projects\third\pbz\pbz6"
    code_files = [
        ("Программный код модуля базы данных (database.py):", os.path.join(base_proj, "database.py")),
        ("Программный код экранных форм и навигации (forms.py):", os.path.join(base_proj, "forms.py")),
        ("Программный код табличного представления, сортировки и поиска (table_view.py):", os.path.join(base_proj, "table_view.py")),
        ("Программный код генератора и просмотрщика аналитических отчетов (reports.py):", os.path.join(base_proj, "reports.py")),
        ("Программный код главного окна приложения (main.py):", os.path.join(base_proj, "main.py")),
    ]
    append_code_modules(doc, code_files)

    img_dir = os.path.join(base_proj, "report_images")
    screenshots = [
        ("Главное окно приложения (Информационная система библиотеки)", os.path.join(img_dir, "win_main.png")),
        ("Экранная форма ввода и навигации по записям с кнопками быстрого перехода «Таблица» и «Отчёт»", os.path.join(img_dir, "win_record_form.png")),
        ("Окно табличного представления данных с сортировкой и фильтрацией", os.path.join(img_dir, "win_table_view.png")),
        ("Результат контекстного поиска данных с цветовой подсветкой строк", os.path.join(img_dir, "win_table_search.png")),
        ("Отчет № 1 «Каталог книжного фонда библиотеки»", os.path.join(img_dir, "win_report1.png")),
        ("Отчет № 2 «Справочник библиотечных отделений и филиалов»", os.path.join(img_dir, "win_report2.png")),
        ("Отчет № 3 «Ведомость распределения экземпляров по залам и филиалам»", os.path.join(img_dir, "win_report3.png")),
        ("Отчет № 4 «Сводный статистический отчет по издательствам»", os.path.join(img_dir, "win_report4.png")),
    ]
    conclusion = (
        "в ходе выполнения лабораторной работы №6 были успешно освоены практические навыки проектирования "
        "табличного пользовательского интерфейса и построения аналитических отчетов для реляционной базы данных библиотеки "
        "(таблицы BOOKS, LIBRARIES, COPIES). Разработана табличная форма с динамической сортировкой по возрастанию и убыванию, "
        "настраиваемой фильтрацией и контекстным поиском с цветовой подсветкой найденных совпадений. На экранные формы добавлены "
        "кнопки быстрого вызова табличного вида и отчетов. Сформированы 4 аналитических отчета со статистическими итогами, "
        "поддержкой предварительного просмотра и возможностью экспорта в форматы HTML и TXT."
    )
    append_screenshots_and_conclusion(doc, screenshots, conclusion)

    doc.save(out_path)
    print(f"Успешно сохранен: {out_path} ({os.path.getsize(out_path)} байт)")

def build_v16():
    out_path = os.path.join(OUT_DIR, "ЛР 6 ПБЗ Антон.docx")
    print(f"Генерация {out_path} (Вариант 16 - Малич А.В.)...")
    doc = docx.Document(TEMPLATE_PATH)

    set_title_page(
        doc,
        lab_num_str=LAB_TITLE,
        topic_str=TOPIC,
        variant_num=16,
        student_line1="Выполнил:",
        student_line2="Студент 3 курса",
        student_name="Малич А.В."
    )

    variant_desc = "Вариант 16: база данных, содержащая таблицы BOOKS (Книги), READERS (Читатели) и LOANS (Выдача книг)."
    tables_meta = [
        ("Таблица BOOKS — каталог книжного фонда библиотечной сети.", [
            ("shifr", "TEXT NOT NULL", "PK_Books (первичный ключ)", "Каталожный шифр книги (напр. КН-101)"),
            ("author", "TEXT NOT NULL", "—", "Фамилия и инициалы автора книги"),
            ("title", "TEXT NOT NULL", "—", "Наименование литературного произведения"),
            ("publisher", "TEXT NOT NULL", "—", "Наименование издательства"),
            ("year", "INTEGER NOT NULL", "CK_Books_Year (year > 0)", "Год публикации издания"),
        ]),
        ("Таблица READERS — картотека зарегистрированных читателей библиотеки.", [
            ("reader_id", "INTEGER NOT NULL", "PK_Readers (первичный ключ)", "Номер читательского билета (напр. 501)"),
            ("full_name", "TEXT NOT NULL", "—", "Фамилия, имя и отчество читателя"),
            ("address", "TEXT NOT NULL", "—", "Адрес фактического проживания"),
            ("phone", "TEXT NOT NULL", "—", "Контактный номер телефона"),
            ("education", "TEXT NOT NULL", "CK_Education (высшее, среднее и др.)", "Уровень образования абонента"),
        ]),
        ("Таблица LOANS — журнал учета выдачи книг читателям на руки.", [
            ("id", "INTEGER NOT NULL", "PK_Loans (AUTOINCREMENT)", "Суррогатный первичный ключ регистрационной записи"),
            ("reader_id", "INTEGER NOT NULL", "FK_Loans_Readers -> readers(reader_id) ON UPDATE CASCADE ON DELETE CASCADE", "Номер читательского билета"),
            ("shifr", "TEXT NOT NULL", "FK_Loans_Books -> books(shifr) ON UPDATE CASCADE ON DELETE CASCADE", "Шифр выданной книги"),
            ("issue_date", "TEXT NOT NULL", "—", "Фактическая дата выдачи книги (ГГГГ-ММ-ДД)"),
            ("return_date", "TEXT NOT NULL", "—", "Контрольный срок возврата книги (ГГГГ-ММ-ДД)"),
        ]),
    ]
    append_common_lab6_intro(doc, variant_desc, tables_meta)

    base_proj = r"D:\study\projects\third\pbz\pbz6\pbz6_16"
    code_files = [
        ("Программный код модуля базы данных (database.py):", os.path.join(base_proj, "database.py")),
        ("Программный код экранных форм и навигации (forms.py):", os.path.join(base_proj, "forms.py")),
        ("Программный код табличного представления, сортировки и поиска (table_view.py):", os.path.join(base_proj, "table_view.py")),
        ("Программный код генератора и просмотрщика аналитических отчетов (reports.py):", os.path.join(base_proj, "reports.py")),
        ("Программный код главного окна приложения (main.py):", os.path.join(base_proj, "main.py")),
    ]
    append_code_modules(doc, code_files)

    img_dir = os.path.join(base_proj, "report_images")
    screenshots = [
        ("Главное окно приложения (Информационная система библиотеки)", os.path.join(img_dir, "win_main.png")),
        ("Экранная форма учета выдачи книг с кнопками «Таблица» и «Отчёт»", os.path.join(img_dir, "win_record_form.png")),
        ("Окно табличного представления данных с сортировкой и фильтрацией", os.path.join(img_dir, "win_table_view.png")),
        ("Результат контекстного поиска данных с цветовой подсветкой строк", os.path.join(img_dir, "win_table_search.png")),
        ("Отчет № 1 «Каталог книжного фонда библиотеки»", os.path.join(img_dir, "win_report1.png")),
        ("Отчет № 2 «Картотека читателей библиотеки»", os.path.join(img_dir, "win_report2.png")),
        ("Отчет № 3 «Журнал учета выдачи книг читателям на руки»", os.path.join(img_dir, "win_report3.png")),
        ("Отчет № 4 «Контрольная ведомость сроков возврата литературы»", os.path.join(img_dir, "win_report4.png")),
    ]
    conclusion = (
        "в ходе выполнения лабораторной работы №6 были успешно сформированы навыки разработки табличного интерфейса "
        "и проектирования аналитических отчетов для информационной системы библиотеки (таблицы BOOKS, READERS, LOANS). "
        "Реализован функционал гибкой многокритериальной сортировки записей по возрастанию и убыванию, фильтрации по уникальным "
        "значениям и контекстного поиска с визуальным выделением совпадений. На экранные формы навигации интегрированы кнопки "
        "перехода «Таблица» и «Отчёт». Внедрены 4 специализированных отчета по фонду, читателям и абонементу с расчетом итоговых "
        "показателей и возможностью экспорта в HTML и TXT."
    )
    append_screenshots_and_conclusion(doc, screenshots, conclusion)

    doc.save(out_path)
    print(f"Успешно сохранен: {out_path} ({os.path.getsize(out_path)} байт)")

def build_v15():
    out_path = os.path.join(OUT_DIR, "ЛР 6 ПБЗ Маковей.docx")
    print(f"Генерация {out_path} (Вариант 15 - Маковей Е.В.)...")
    doc = docx.Document(TEMPLATE_PATH)

    set_title_page(
        doc,
        lab_num_str=LAB_TITLE,
        topic_str=TOPIC,
        variant_num=15,
        student_line1="Выполнил:",
        student_line2="Студент 3 курса",
        student_name="Маковей Е.В."
    )

    variant_desc = "Вариант 15: база данных, содержащая таблицы Склады (Sklady), Производители (Proizvoditeli) и Товары (Tovary)."
    tables_meta = [
        ("Таблица Склады — перечень складских комплексов и филиалов.", [
            ("KodSklada", "INT PRIMARY KEY AUTOINCREMENT", "PK_Sklady (первичный ключ)", "Уникальный числовой код складского комплекса"),
            ("Adres", "NVARCHAR(50) NOT NULL", "— (непустая строка)", "Фактический адрес расположения склада"),
            ("Telefon", "NVARCHAR(20) NOT NULL", "—", "Контактный номер телефона администрации склада"),
            ("Firma", "NVARCHAR(30) NOT NULL", "—", "Наименование юридического лица / фирмы-владельца"),
        ]),
        ("Таблица Производители — реестр заводов-изготовителей продукции.", [
            ("KodProiz", "INT PRIMARY KEY AUTOINCREMENT", "PK_Proizvoditeli (первичный ключ)", "Уникальный идентификатор производителя"),
            ("NameProiz", "NVARCHAR(40) NOT NULL", "— (непустая строка)", "Наименование завода-изготовителя / поставщика"),
            ("AdresProiz", "NVARCHAR(50) NOT NULL", "—", "Юридический адрес предприятия-изготовителя"),
            ("TelefonProiz", "NVARCHAR(20) NOT NULL", "—", "Телефон отдела оптовых продаж и поставок"),
            ("Strana", "NVARCHAR(25) NOT NULL", "—", "Страна происхождения продукции"),
        ]),
        ("Таблица Товары — номенклатура и количественный учет складских запасов.", [
            ("KodTovara", "INT PRIMARY KEY AUTOINCREMENT", "PK_Tovary (первичный ключ)", "Уникальный идентификационный код товара"),
            ("KodSklada", "INT NOT NULL", "FK_Tovary_Sklady → dbo.Склады ON UPDATE/DELETE CASCADE", "Внешний ключ: склад фактического размещения товара"),
            ("KodProiz", "INT NOT NULL", "FK_Tovary_Proiz → dbo.Производители ON UPDATE/DELETE CASCADE", "Внешний ключ: код завода-производителя товара"),
            ("NameT", "NVARCHAR(40) NOT NULL", "— (непустая строка)", "Торговое наименование изделия или материала"),
            ("Edizmer", "NVARCHAR(10) NOT NULL", "—", "Единица измерения (шт, мешок, комплект, кг, упаковка)"),
            ("Kol", "INT NOT NULL", "CK_Tovary_Kol (Kol >= 0)", "Текущий фактический остаток продукции на складе"),
        ]),
    ]
    append_common_lab6_intro(doc, variant_desc, tables_meta)

    base_proj = r"D:\study\projects\third\pbz\pbz6\pbz6_15"
    code_files = [
        ("Программный код модуля базы данных (database.py):", os.path.join(base_proj, "database.py")),
        ("Программный код экранных форм и навигации (forms.py):", os.path.join(base_proj, "forms.py")),
        ("Программный код табличного представления, сортировки и поиска (table_view.py):", os.path.join(base_proj, "table_view.py")),
        ("Программный код генератора и просмотрщика аналитических отчетов (reports.py):", os.path.join(base_proj, "reports.py")),
        ("Программный код главного окна приложения (main.py):", os.path.join(base_proj, "main.py")),
    ]
    append_code_modules(doc, code_files)

    img_dir = os.path.join(base_proj, "report_images")
    screenshots = [
        ("Главное окно приложения (Информационная система склада товаров)", os.path.join(img_dir, "win_main.png")),
        ("Экранная форма учета товаров с кнопками «Таблица» и «Отчёт»", os.path.join(img_dir, "win_record_form.png")),
        ("Окно табличного представления данных склада с сортировкой и фильтрацией", os.path.join(img_dir, "win_table_view.png")),
        ("Результат контекстного поиска по складу с цветовой подсветкой строк", os.path.join(img_dir, "win_table_search.png")),
        ("Отчет № 1 «Ведомость складских остатков и номенклатуры продукции»", os.path.join(img_dir, "win_report1.png")),
        ("Отчет № 2 «Справочник складских комплексов и емкостей хранения»", os.path.join(img_dir, "win_report2.png")),
        ("Отчет № 3 «Реестр заводов-производителей и стран происхождения»", os.path.join(img_dir, "win_report3.png")),
        ("Отчет № 4 «Сводная инвентаризационная ведомость по складам»", os.path.join(img_dir, "win_report4.png")),
    ]
    conclusion = (
        "в ходе выполнения лабораторной работы №6 были успешно приобретены практические навыки создания "
        "табличного пользовательского интерфейса и построения многофункциональных аналитических отчетов для реляционной базы данных "
        "складского учета (таблицы Склады, Производители, Товары). Разработан модуль табличного представления с возможностью "
        "сортировки по возрастанию и убыванию, фильтрации по уникальным значениям и контекстного поиска с подсветкой результатов. "
        "На экранных формах реализованы кнопки перехода «Таблица» и «Отчёт». Сформированы 4 аналитических отчета с расчетом итоговых "
        "сводок и экспортом в форматы HTML и TXT."
    )
    append_screenshots_and_conclusion(doc, screenshots, conclusion)

    doc.save(out_path)
    print(f"Успешно сохранен: {out_path} ({os.path.getsize(out_path)} байт)")

if __name__ == "__main__":
    build_v17()
    build_v16()
    build_v15()
    print("Все 3 отчета успешно сгенерированы!")
