# zeroshell.py - Интерпретатор ZeroBasics
import os
import sys
import time
import random
import platform

# Проверяем наличие библиотек
try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    COLOR_SUPPORT = True
except ImportError:
    COLOR_SUPPORT = False

class ZeroShell:
    def __init__(self):
        self.variables = {}
        self.chapters = {}
        self.current_chapter = None
        self.chapter_stack = []
        self.script_dir = "Scripts"
        self.project_dir = None
        self.should_exit = False
        
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_colored(self, text, color="white"):
        """Вывод цветного текста"""
        if COLOR_SUPPORT:
            colors = {
                "black": Fore.BLACK,
                "red": Fore.RED,
                "green": Fore.GREEN,
                "yellow": Fore.YELLOW,
                "blue": Fore.BLUE,
                "magenta": Fore.MAGENTA,
                "cyan": Fore.CYAN,
                "white": Fore.WHITE,
                "reset": Style.RESET_ALL
            }
            color_code = colors.get(color.lower(), Fore.WHITE)
            print(f"{color_code}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def parse_value(self, value_str):
        """Парсит значение, подставляя переменные"""
        if not value_str:
            return ""
            
        result = ""
        i = 0
        while i < len(value_str):
            if value_str[i] == '$' and i+1 < len(value_str) and (value_str[i+1].isalnum() or value_str[i+1] == '_'):
                j = i + 1
                while j < len(value_str) and (value_str[j].isalnum() or value_str[j] == '_'):
                    j += 1
                var_name = value_str[i+1:j]
                var_value = self.variables.get(var_name, "")
                result += str(var_value)
                i = j
            else:
                result += value_str[i]
                i += 1
        return result
    
    def parse_text(self, text):
        """Парсит текст с фигурными скобками и переменными - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        if not text:
            return ""
            
        # Убираем окружающие фигурные скобки если текст полностью в них
        if text.startswith('{') and text.endswith('}'):
            text = text[1:-1]
            
        result = ""
        i = 0
        length = len(text)
        
        while i < length:
            # Если находим открывающую скобку
            if text[i] == '{':
                # Ищем закрывающую скобку
                brace_count = 1
                j = i + 1
                while j < length and brace_count > 0:
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                    j += 1
                
                if brace_count == 0:
                    # Нашли парную закрывающую скобку
                    inner_text = text[i+1:j-1]
                    # Обрабатываем внутренний текст на предмет переменных
                    inner_result = ""
                    k = 0
                    while k < len(inner_text):
                        if inner_text[k] == '$' and k+1 < len(inner_text) and (inner_text[k+1].isalnum() or inner_text[k+1] == '_'):
                            m = k + 1
                            while m < len(inner_text) and (inner_text[m].isalnum() or inner_text[m] == '_'):
                                m += 1
                            var_name = inner_text[k+1:m]
                            inner_result += str(self.variables.get(var_name, ""))
                            k = m
                        else:
                            inner_result += inner_text[k]
                            k += 1
                    result += inner_result
                    i = j
                else:
                    # Непарная открывающая скобка, оставляем как есть
                    result += text[i]
                    i += 1
            elif text[i] == '$' and i+1 < length and (text[i+1].isalnum() or text[i+1] == '_'):
                # Обработка переменных вне скобок
                j = i + 1
                while j < length and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                var_name = text[i+1:j]
                result += str(self.variables.get(var_name, ""))
                i = j
            else:
                # Обычный текст
                result += text[i]
                i += 1
        
        return result
    
    def execute_command(self, line):
        """Выполняет одну команду ZeroBasics"""
        line = line.strip()
        if not line:
            return True
            
        # Удаляем комментарии
        if '#' in line:
            line = line.split('#')[0].strip()
            if not line:
                return True
        
        # Разделяем команду на слова, но сохраняем строки в фигурных скобках
        parts = []
        current_part = ""
        i = 0
        in_braces = False
        brace_depth = 0
        
        while i < len(line):
            char = line[i]
            
            if char == '{':
                if not in_braces:
                    in_braces = True
                brace_depth += 1
                current_part += char
            elif char == '}':
                brace_depth -= 1
                current_part += char
                if brace_depth == 0:
                    in_braces = False
            elif char == ' ' and not in_braces:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        if not parts:
            return True
            
        cmd = parts[0].lower()
        
        # Обработка команды Print
        if cmd == "print":
            output_lines = []
            current_line = ""
            current_color = None
            i = 1
            
            while i < len(parts):
                token = parts[i]
                
                if token.lower() == "nline":
                    if current_line:
                        output_lines.append((current_line.strip(), current_color))
                    output_lines.append(("\n", None))
                    current_line = ""
                    current_color = None
                elif token.lower() == "col" and i+1 < len(parts):
                    if current_line:
                        output_lines.append((current_line.strip(), current_color))
                        current_line = ""
                    i += 1
                    current_color = parts[i]
                else:
                    parsed_token = self.parse_text(token)
                    if current_line:
                        current_line += " " + parsed_token
                    else:
                        current_line = parsed_token
                i += 1
            
            if current_line:
                output_lines.append((current_line.strip(), current_color))
            
            # Выводим результат
            for text, color in output_lines:
                if text == "\n":
                    print()
                elif color and COLOR_SUPPORT:
                    self.print_colored(text, color)
                else:
                    print(text)
        
        # Обработка команды Input
        elif cmd == "input":
            if len(parts) < 2:
                return True
                
            var_name = parts[1]
            if var_name.startswith('$'):
                var_name = var_name[1:]
            
            prompt = ""
            limit = None
            
            # Ищем подсказку после '-'
            dash_found = False
            prompt_parts = []
            
            for i in range(2, len(parts)):
                if parts[i] == '-':
                    dash_found = True
                elif dash_found:
                    prompt_parts.append(parts[i])
            
            if prompt_parts:
                prompt = " ".join(prompt_parts)
                prompt = self.parse_text(prompt)
                
                # Проверяем на лимит (L10)
                for part in prompt_parts:
                    if part.lower().startswith('l') and part[1:].isdigit():
                        limit = int(part[1:])
                        break
            
            if prompt:
                user_input = input(prompt + " ")
            else:
                user_input = input("Ввод: ")
                
            if limit and len(user_input) > limit:
                user_input = user_input[:limit]
            
            self.variables[var_name] = user_input
        
        # Обработка команды Chp
        elif cmd == "chp":
            if len(parts) > 1:
                chapter_name = parts[1]
                self.chapters[chapter_name] = []
                self.current_chapter = chapter_name
        
        # Обработка команды End Chp
        elif cmd == "end" and len(parts) > 1 and parts[1].lower() == "chp":
            self.current_chapter = None
        
        # Обработка присваивания переменной
        elif len(parts) >= 3 and parts[1] == '=':
            var_name = parts[0]
            if var_name.startswith('$'):
                var_name = var_name[1:]
                value_parts = parts[2:]
                value_expr = " ".join(value_parts)
                
                # Заменяем переменные в выражении
                value = ""
                i = 0
                while i < len(value_expr):
                    if value_expr[i] == '$' and i+1 < len(value_expr) and (value_expr[i+1].isalnum() or value_expr[i+1] == '_'):
                        j = i + 1
                        while j < len(value_expr) and (value_expr[j].isalnum() or value_expr[j] == '_'):
                            j += 1
                        var_name_in_expr = value_expr[i+1:j]
                        value += str(self.variables.get(var_name_in_expr, ""))
                        i = j
                    else:
                        value += value_expr[i]
                        i += 1
                
                self.variables[var_name] = value
        
        # Обработка условия if
        elif cmd == "if":
            # Формат: if $var = {значение} - команда
            if len(parts) >= 4 and parts[2] == '=':
                var_name = parts[1]
                if var_name.startswith('$'):
                    var_name = var_name[1:]
                
                # Находим позицию '-'
                dash_pos = -1
                for idx in range(len(parts)):
                    if parts[idx] == '-':
                        dash_pos = idx
                        break
                
                if dash_pos > 3:
                    # Собираем значение (может быть несколько частей)
                    value_parts = parts[3:dash_pos]
                    value = " ".join(value_parts)
                    value = self.parse_text(value)
                    
                    # Собираем команду
                    command_parts = parts[dash_pos+1:]
                    command = " ".join(command_parts)
                    
                    if self.variables.get(var_name, "") == value:
                        return self.execute_command(command)
        
        # Обработка команды Calc
        elif cmd == "calc":
            if len(parts) >= 5:
                try:
                    # Формат: calc $a + $b - $result
                    expr_parts = parts[1:-2]  # Все кроме последних двух частей
                    result_var = parts[-1]
                    if result_var.startswith('$'):
                        result_var = result_var[1:]
                    
                    # Собираем выражение
                    expr = " ".join(expr_parts)
                    
                    # Заменяем переменные на их значения
                    for var_name, var_value in self.variables.items():
                        expr = expr.replace(f'${var_name}', var_value)
                    
                    # Вычисляем
                    try:
                        result = eval(expr)
                        self.variables[result_var] = str(result)
                    except:
                        self.variables[result_var] = "0"
                except:
                    pass
        
        # Обработка команды Rpl
        elif cmd == "rpl":
            if len(parts) >= 3:
                count_str = parts[1]
                try:
                    if count_str.startswith('$'):
                        count = int(self.variables.get(count_str[1:], 0))
                    else:
                        count = int(count_str)
                    
                    command = " ".join(parts[2:])
                    for _ in range(count):
                        if not self.execute_command(command):
                            break
                except:
                    pass
        
        # Обработка команды Wait
        elif cmd == "wait":
            if len(parts) > 1:
                time_str = parts[1]
                try:
                    if time_str.startswith('$'):
                        wait_time = float(self.variables.get(time_str[1:], 0))
                    else:
                        wait_time = float(time_str)
                    time.sleep(wait_time)
                except:
                    pass
        
        # Обработка команды Exit
        elif cmd == "exit":
            self.should_exit = True
            return False
        
        # Обработка If Pressed
        elif cmd == "if" and len(parts) > 1 and parts[1].lower() == "pressed":
            # Упрощенная версия для демонстрации
            if len(parts) >= 4:
                key = parts[2].strip('{}')
                command = " ".join(parts[4:])
                print(f"Для тестирования: предполагается нажатие клавиши {key}")
                print(f"Выполняем команду: {command}")
                return self.execute_command(command)
        
        # Обработка команды Random
        elif cmd == "random":
            if len(parts) >= 4 and parts[2] == '-':
                range_str = parts[1]
                var_name = parts[3]
                if var_name.startswith('$'):
                    var_name = var_name[1:]
                
                if ',' in range_str:
                    items = [item.strip() for item in range_str.split(',')]
                    try:
                        # Если диапазон чисел
                        if len(items) == 2:
                            try:
                                start = int(items[0])
                                end = int(items[1])
                                result = random.randint(start, end)
                            except:
                                result = random.choice(items)
                        else:
                            result = random.choice(items)
                    except:
                        result = random.choice(items)
                else:
                    result = range_str
                
                self.variables[var_name] = str(result)
        
        # Обработка команды Save
        elif cmd == "save":
            if len(parts) >= 5:
                var_name = parts[1]
                if var_name.startswith('$'):
                    var_name = var_name[1:]
                
                # Ищем конструкцию "in ... - filename"
                try:
                    in_index = parts.index("in")
                    dash_index = parts.index("-", in_index + 1)
                    
                    if in_index < dash_index < len(parts):
                        location = parts[in_index + 1]
                        filename = " ".join(parts[dash_index + 1:])
                        filename = self.parse_text(filename)
                        
                        if location.lower() == "here":
                            if self.project_dir:
                                save_path = os.path.join(self.project_dir, filename)
                            else:
                                save_path = filename
                        else:
                            save_path = os.path.join(location, filename)
                        
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        
                        with open(save_path, 'w', encoding='utf-8') as f:
                            f.write(self.variables.get(var_name, ""))
                        print(f"Сохранено: {save_path}")
                except ValueError:
                    pass
        
        # Обработка If Not Found Create
        elif len(parts) >= 5 and parts[0] == "if" and parts[1] == "not" and parts[2] == "found" and parts[3] == "create":
            folder_name = " ".join(parts[4:])
            folder_name = self.parse_text(folder_name)
            if not os.path.exists(folder_name):
                os.makedirs(folder_name, exist_ok=True)
                print(f"Создана папка: {folder_name}")
        
        # Обработка команды Con
        elif cmd == "con":
            if len(parts) > 1:
                system_cmd = " ".join(parts[1:])
                if system_cmd.startswith('!'):
                    os.system(system_cmd[1:])
        
        # Обработка команды Run
        elif cmd == "run":
            if len(parts) > 1:
                chapter_name = parts[1]
                if chapter_name in self.chapters:
                    if self.current_chapter:
                        self.chapter_stack.append(self.current_chapter)
                    self.execute_chapter(chapter_name)
        
        return True
    
    def execute_chapter(self, chapter_name):
        """Выполняет главу скрипта"""
        if chapter_name in self.chapters:
            self.current_chapter = chapter_name
            for line in self.chapters[chapter_name]:
                if not self.execute_command(line):
                    return False
                if self.should_exit:
                    return False
            return True
        return False
    
    def load_script(self, filename):
        """Загружает и парсит скрипт"""
        # Сбрасываем состояние
        self.variables.clear()
        self.chapters.clear()
        self.current_chapter = None
        self.chapter_stack.clear()
        self.should_exit = False
        
        # Полный путь к файлу
        filepath = os.path.join(self.script_dir, filename)
        if not os.path.exists(filepath):
            # Пробуем добавить .txt если не указано расширение
            if not filename.lower().endswith('.txt'):
                filepath_txt = os.path.join(self.script_dir, filename + '.txt')
                if os.path.exists(filepath_txt):
                    filepath = filepath_txt
                else:
                    print(f"Файл {filename} не найден в {self.script_dir}")
                    return False
            else:
                print(f"Файл {filename} не найден в {self.script_dir}")
                return False
        
        # Создаем папку для проекта
        script_name = os.path.splitext(os.path.basename(filepath))[0]
        self.project_dir = os.path.join(self.script_dir, "projects", script_name)
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Читаем скрипт
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            print(f"Ошибка чтения файла: {filename}")
            return False
        
        # Парсим скрипт на главы
        current_chapter = None
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Проверяем комментарии
            if line.startswith('#'):
                continue
            
            # Проверяем начало главы
            if line.lower().startswith("chp "):
                chapter_name = line[4:].strip()
                current_chapter = chapter_name
                self.chapters[current_chapter] = []
            # Проверяем конец главы
            elif line.lower() == "end chp":
                current_chapter = None
            # Добавляем команду в текущую главу
            elif current_chapter is not None:
                self.chapters[current_chapter].append(line)
            # Если команды вне главы, создаем главу "main"
            else:
                if not self.chapters:
                    current_chapter = "main"
                    self.chapters[current_chapter] = [line]
                else:
                    # Если уже есть главы, добавляем в последнюю
                    last_chapter = list(self.chapters.keys())[-1]
                    self.chapters[last_chapter].append(line)
        
        return True
    
    def run_script(self, filename):
        """Запускает скрипт"""
        print(f"\nЗагрузка скрипта: {filename}")
        print("=" * 50)
        
        if not self.load_script(filename):
            print(f"Не удалось загрузить скрипт: {filename}")
            return False
        
        if not self.chapters:
            print("Скрипт не содержит команд")
            return False
        
        # Запускаем первую главу
        first_chapter = list(self.chapters.keys())[0]
        result = self.execute_chapter(first_chapter)
        
        print("=" * 50)
        return result
    
    def shell_mode(self):
        """Интерактивный режим оболочки"""
        self.clear_screen()
        print("=" * 60)
        print("ZeroShell 0.10 - Интерпретатор ZeroBasics")
        print("=" * 60)
        print("Введите !Help для справки")
        print("-" * 60)
        
        while True:
            try:
                # Показываем текущую директорию скриптов
                if os.path.exists(self.script_dir):
                    script_count = len([f for f in os.listdir(self.script_dir) if f.endswith('.txt')])
                    prompt = f"ZB[{script_count} скриптов]> "
                else:
                    prompt = "ZB[нет папки Scripts]> "
                
                cmd = input(prompt).strip()
                
                if not cmd:
                    continue
                
                # Команды оболочки
                if cmd.lower() == "!exit":
                    print("Выход из ZeroShell...")
                    break
                
                elif cmd.lower() == "!help":
                    print("\n" + "=" * 60)
                    print("КОМАНДЫ ZEROSHELL:")
                    print("=" * 60)
                    print("!Run <script>    - Запустить скрипт")
                    print("!List            - Список скриптов")
                    print("!New <name>      - Создать новый скрипт")
                    print("!Edit <script>   - Редактировать скрипт")
                    print("!Clear           - Очистить экран")
                    print("!Dir             - Показать папку скриптов")
                    print("!Help            - Эта справка")
                    print("!Exit            - Выход")
                    print("=" * 60)
                    print("\nСКРИПТЫ ХРАНЯТСЯ В ПАПКЕ: Scripts/")
                    print("Пример: !Run calculator.txt")
                    print("=" * 60)
                
                elif cmd.lower().startswith("!run "):
                    script_name = cmd[5:].strip()
                    if script_name:
                        self.run_script(script_name)
                        input("\nНажмите Enter чтобы продолжить...")
                        self.clear_screen()
                        print("ZeroShell 0.10 - Интерпретатор ZeroBasics")
                        print("=" * 60)
                    else:
                        print("Укажите имя скрипта: !Run myscript.txt")
                
                elif cmd.lower() == "!list":
                    print("\n" + "=" * 60)
                    print("СКРИПТЫ В ПАПКЕ Scripts:")
                    print("=" * 60)
                    
                    if not os.path.exists(self.script_dir):
                        print("Папка Scripts не найдена!")
                        print("Создайте папку 'Scripts' в текущей директории.")
                    else:
                        txt_files = [f for f in os.listdir(self.script_dir) if f.endswith('.txt')]
                        if txt_files:
                            for i, file in enumerate(sorted(txt_files), 1):
                                filepath = os.path.join(self.script_dir, file)
                                try:
                                    size = os.path.getsize(filepath)
                                except:
                                    size = 0
                                print(f"{i:3}. {file:30} ({size} байт)")
                        else:
                            print("Нет скриптов. Создайте новый: !New myscript")
                        print("=" * 60)
                
                elif cmd.lower().startswith("!new "):
                    script_name = cmd[5:].strip()
                    if script_name:
                        if not script_name.endswith('.txt'):
                            script_name += '.txt'
                        
                        filepath = os.path.join(self.script_dir, script_name)
                        if os.path.exists(filepath):
                            print(f"Скрипт {script_name} уже существует!")
                        else:
                            # Создаем шаблон скрипта
                            template = """Chp main
Print {Добро пожаловать в программу!}
Print Nline {Это ваш новый скрипт.}
Input $name - {Введите ваше имя: }
Print {Привет, } $name {!}
Wait 2
End Chp"""
                            
                            os.makedirs(self.script_dir, exist_ok=True)
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(template)
                            print(f"Создан новый скрипт: {script_name}")
                            print(f"Путь: {filepath}")
                    else:
                        print("Укажите имя скрипта: !New myscript")
                
                elif cmd.lower().startswith("!edit "):
                    script_name = cmd[6:].strip()
                    if script_name:
                        if not script_name.endswith('.txt'):
                            script_name += '.txt'
                        
                        filepath = os.path.join(self.script_dir, script_name)
                        if os.path.exists(filepath):
                            print(f"Редактирование: {script_name}")
                            print("Содержимое файла:")
                            print("-" * 40)
                            try:
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                print(content)
                            except:
                                print("Не удалось прочитать файл")
                            print("-" * 40)
                            print("Используйте внешний редактор для редактирования.")
                        else:
                            print(f"Скрипт {script_name} не найден!")
                    else:
                        print("Укажите имя скрипта: !Edit myscript.txt")
                
                elif cmd.lower() == "!clear":
                    self.clear_screen()
                    print("ZeroShell 0.10 - Интерпретатор ZeroBasics")
                    print("=" * 60)
                
                elif cmd.lower() == "!dir":
                    print("\n" + "=" * 60)
                    print("ИНФОРМАЦИЯ О ПАПКЕ SCRIPTS:")
                    print("=" * 60)
                    if os.path.exists(self.script_dir):
                        abs_path = os.path.abspath(self.script_dir)
                        print(f"Путь: {abs_path}")
                        
                        txt_files = [f for f in os.listdir(self.script_dir) if f.endswith('.txt')]
                        projects_dir = os.path.join(self.script_dir, "projects")
                        
                        print(f"Скриптов: {len(txt_files)}")
                        if os.path.exists(projects_dir):
                            try:
                                projects = os.listdir(projects_dir)
                                print(f"Проектов: {len(projects)}")
                            except:
                                print("Проектов: 0")
                        print("=" * 60)
                    else:
                        print("Папка Scripts не найдена!")
                        print("Создайте папку 'Scripts' для хранения скриптов.")
                        print("=" * 60)
                
                else:
                    # Пробуем выполнить как команду ZeroBasics
                    self.execute_command(cmd)
            
            except KeyboardInterrupt:
                print("\n\nВыход из ZeroShell...")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

def main():
    """Главная функция"""
    # Создаем папку Scripts если ее нет
    if not os.path.exists("Scripts"):
        os.makedirs("Scripts", exist_ok=True)
        print("Создана папка 'Scripts' для ваших скриптов")
        print("Скрипты должны быть в формате .txt")
        
        # Создаем пример скрипта
        example_script = """Chp main
Print {Тестовый скрипт ZeroShell}
Print Nline {Демонстрация работы}
Print Col green {Зеленый текст}
Print Nline Col red {Красный текст на новой строке}
Input $name - {Введите ваше имя: }
Print {Привет, } $name {!}
Wait 1
Print Nline {Спасибо за использование ZeroShell!}
End Chp"""
        
        with open(os.path.join("Scripts", "test.txt"), 'w', encoding='utf-8') as f:
            f.write(example_script)
        print("Создан пример скрипта: Scripts/test.txt")
    
    # Создаем папку projects внутри Scripts
    projects_dir = os.path.join("Scripts", "projects")
    if not os.path.exists(projects_dir):
        os.makedirs(projects_dir, exist_ok=True)
    
    shell = ZeroShell()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Запуск скрипта напрямую
        script_name = sys.argv[1]
        shell.run_script(script_name)
        
        # Ждем нажатия Enter перед выходом
        if platform.system() == "Windows":
            input("\nНажмите Enter для выхода...")
    else:
        # Запускаем интерактивный режим
        shell.shell_mode()

if __name__ == "__main__":
    main()