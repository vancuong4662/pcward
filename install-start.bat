@echo off
echo ===============================
echo Bat dau chay chuong trinh Python...
echo ===============================

:: Kiem tra Python da cai dat chua
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Khong tim thay Python. Vui long cai dat Python truoc khi chay script nay.
    pause
    exit /b
)

:: Kiem tra file requirements.txt va cai dat neu co
if exist requirements.txt (
    echo Dang cai dat cac thu vien can thiet tu requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
)

:: Kiem tra file main.py co ton tai khong
if not exist main.py (
    echo Khong tim thay file main.py trong thu muc hien tai.
    pause
    exit /b
)

:: Chay chuong trinh Python
python main.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo Xay ra loi khi chay chuong trinh Python.
) else (
    echo.
    echo Chuong trinh chay thanh cong!
)

echo ===============================
echo Nhan phim bat ky de thoat...
pause >nul