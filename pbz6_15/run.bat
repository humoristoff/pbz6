@echo off
chcp 65001 > nul
title АСУ Склад товаров - Лабораторная работа №6 (Вариант 15)
echo Запуск приложения "АСУ Склад товаров" (ЛР 6)...
python main.py
if errorlevel 1 (
    echo.
    echo Попытка запуска через py -3.11...
    py -3.11 main.py
)
pause
