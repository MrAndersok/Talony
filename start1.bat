@echo off
SETLOCAL

:: ====== Шлях до встановленого Python ======
set PYTHON_PATH=%LocalAppData%\Programs\Python\Python311\python.exe

:: ====== Перевіряємо, чи встановлений Python ======
if exist "%PYTHON_PATH%" (
    echo Python знайдено: %PYTHON_PATH%
) else (
    echo Python не знайдено. Завантаження та встановлення...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe -OutFile python-installer.exe"
    python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    del python-installer.exe
)

:: ====== Оновлення pip ======
echo Оновлення pip...
"%PYTHON_PATH%" -m pip install --upgrade pip

:: ====== Встановлення необхідних бібліотек ======
echo Встановлення необхідних бібліотек...
"%PYTHON_PATH%" -m pip install pyqt6 reportlab

:: ==== Додати інші бібліотеки за потреби ====
:: "%PYTHON_PATH%" -m pip install pillow pandas ...

:: ====== Запуск програми ======
echo Запуск програми...
start "" "%PYTHON_PATH%" main.py

:: Завершення
echo Готово!
pause
ENDLOCAL
