# install.py
import os
import sys
import platform

def print_banner():
    print("=" * 60)
    print("Установка ZeroShell 0.10")
    print("Интерпретатор языка ZeroBasics")
    print("=" * 60)

def check_python():
    print("\nПроверка версии Python...")
    if sys.version_info < (3, 6):
        print(f"  Ошибка: У вас Python {sys.version_info.major}.{sys.version_info.minor}")
        print("  Требуется Python 3.6 или выше")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def install_dependencies():
    print("\nПроверка зависимостей...")
    try:
        import colorama
        print("  ✓ colorama уже установлен")
    except ImportError:
        print("  Установка colorama для цветного вывода...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            print("  ✓ colorama установлен")
        except:
            print("  ✗ Не удалось установить colorama (можно работать без него)")

def create_directory_structure():
    print("\nСоздание структуры папок...")
    
    directories = [
        "скрипты",
        "скрипты/projects",
        "скрипты/files"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"  Создана: {directory}")
        else:
            print(f"  Уже существует: {directory}")

def create_example_scripts():
    print("\nСоздание примеров скриптов...")
    
    examples = {
        "calc.txt": """chp main
print {Добро пожаловать в калькулятор!}
print nline {Введите два числа для сложения:}
input $num1 - {Первое число: }
input $num2 - {Второе число: }
calc $num1 + $num2 - $result
print {Результат: } $result
wait 1
print nline {Хотите повторить?}
input $choice - {y/n: }
if $choice = {y} - run main
if $choice = {n} - exit
end chp""",
        
        "notepad.txt": """chp main
print {Блокнот ZeroBasics}
print nline {Введите текст:}
input $text - {Текст: }
print nline {Нажмите Ctrl+S для сохранения}
wait 1
if not found create files
save $text in files - note.txt
print {Текст сохранен в files/note.txt}
wait 2
end chp""",
        
        "game.txt": """chp start
print col red {УГАДАЙ ЧИСЛО}
print nline col green {Компьютер загадал число от 1 до 10}
random 1,10 - $secret
chp game
input $guess - {Ваша догадка (1-10): }
if $guess = $secret - run win
print {Попробуйте еще раз!}
run game
chp win
print col yellow {Поздравляем! Вы угадали число!}
wait 2
input $playagain - {Играть еще? (y/n): }
if $playagain = {y} - run start
exit
end chp"""
    }
    
    for filename, content in examples.items():
        filepath = os.path.join("скрипты", filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Создан: {filename}")
        else:
            print(f"  Уже существует: {filename}")

def create_launcher():
    print("\nСоздание файлов запуска...")
    
    # Для Windows
    if platform.system() == "Windows":
        with open("запуск.bat", "w", encoding="cp866") as f:
            f.write("""@echo off
chcp 65001 > nul
echo Запуск ZeroShell...
python zeroshell.py
if errorlevel 1 pause""")
        print("  Создан: запуск.bat")
        
        with open("запустить_скрипт.bat", "w", encoding="cp866") as f:
            f.write("""@echo off
chcp 65001 > nul
echo Запуск скрипта в ZeroShell...
echo.
if "%~1"=="" (
    echo Использование: запустить_скрипт.bat имя_скрипта
    echo Пример: запустить_скрипт.bat calc.txt
    pause
    exit /b 1
)
python zeroshell.py %1
pause""")
        print("  Создан: запустить_скрипт.bat")
    
    # Для Linux/Mac
    with open("zeroshell.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Запуск ZeroShell..."
python3 zeroshell.py "$@"
""")
    print("  Создан: zeroshell.sh")
    
    # Делаем скрипт исполняемым (для Linux/Mac)
    if platform.system() != "Windows":
        import stat
        os.chmod("zeroshell.sh", stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)

def create_readme():
    print("\nСоздание документации...")
    
    readme_content = """# ZeroShell 0.10

Интерпретатор языка программирования ZeroBasics.

## Быстрый старт

### Windows:
1. Дважды щелкните `запуск.bat`
2. Введите `!Run calc.txt` для запуска калькулятора

Или запустите скрипт напрямую: