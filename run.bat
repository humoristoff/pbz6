@echo off
chcp 65001 > nul
title АСУ Библиотека - Лабораторная работа №6 (Вариант 17)
echo Запуск приложения "АСУ Библиотека" (ЛР 6)...
python main.py
if errorlevel 1 (
    echo.
    echo Попытка запуска через py -3.11...
    py -3.11 main.py
)
pause
