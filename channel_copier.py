from colorama import Fore, Back, Style, init
import urllib.request
import urllib.error
import json
import ssl
import time
import base64
import os
import aiohttp
import asyncio

init(autoreset=True)

# Определяем цвета как переменные
BLUE = Fore.BLUE
CYAN = Fore.CYAN
WHITE = Fore.WHITE
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
MAGENTA = Fore.MAGENTA
BLACK_BG = Back.BLACK

def line(width=65):
    return BLUE + "═" * width

def header(text):
    print(f"\n{BLUE}{'═' * 65}")
    print(f"{CYAN}{text}")
    print(f"{BLUE}{'═' * 65}")

def info(text):
    print(f"{CYAN}• {WHITE}{text}")

def success(text):
    print(f"{GREEN}✓ {WHITE}{text}")

def warning(text):
    print(f"{YELLOW}! {WHITE}{text}")

def error(text):
    print(f"{RED}✖ {WHITE}{text}")

def input_prompt(text):
    return input(f"{CYAN}[?] {text}{WHITE}")

def input_field(text):
    return input(f"{CYAN}>> {text}: {WHITE}")

def print_banner():
    header("✨ DISCORD SERVER CLONER V3 — BLUE EDITION ✨")
    print(f"{WHITE}👤 Автор: {CYAN}zlafik")
    print(f"{WHITE}📞 Discord: {CYAN}zlafik")
    print(f"{WHITE}📱 Telegram: {CYAN}@zlafik")
    print(f"{WHITE}📢 Канал: {CYAN}@biozlafik")
    print(line())
    print(f"{BLUE}🎯 Возможности программы:")
    info("Полное клонирование структуры сервера")
    info("Сохранение ролей, каналов и категорий")
    info("Чистый улучшенный интерфейс")
    info("Удобные подсказки и информативные уведомления")
    print(line())

def print_user_agreement():
    header("📜 ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ")
    warning("ВНИМАТЕЛЬНО ПРОЧИТАЙТЕ ПЕРЕД ИСПОЛЬЗОВАНИЕМ:")
    info("1. Вы несете полную ответственность за использование программы")
    info("2. Разработчик не несет ответственности за последствия")
    info("3. Использование программы осуществляется на свой риск")
    info("4. Запрещено использовать программу во вред другим пользователям")
    print(line())
    error("⚠️  ПРИНИМАЯ СОГЛАШЕНИЕ, ВЫ ПОДТВЕРЖДАЕТЕ ПОЛНОЕ ПОНИМАНИЕ РИСКОВ")
    print(line())

def confirm_agreement():
    print_user_agreement()
    confirmation = input_prompt("Для подтверждения введите: 'Подтвердить - zlafik'\n>> ").strip()
    return confirmation == "Подтвердить - zlafik"

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class AdvancedCloner:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.rate_limit_delay = 0.5
    
    def make_request(self, method, url, data=None):
        try:
            if data:
                data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers=self.headers,
                method=method
            )
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                if response_data:
                    return response, json.loads(response_data)
                else:
                    return response, None
                    
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get('Retry-After', 2)
                warning(f"Rate limit, ждем {retry_after} секунд...")
                time.sleep(float(retry_after))
                return self.make_request(method, url, data)
            error(f"HTTP Error {e.code}: {e.reason}")
            if e.code == 401:
                error("Неверный токен!")
            elif e.code == 403:
                error("Нет прав доступа!")
            return e, None
        except Exception as e:
            error(f"Request Error: {e}")
            return None, e
    
    def get_server_info(self, server_id):
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}')
        if response and response.status == 200:
            return data
        return None
    
    def get_servers(self):
        response, data = self.make_request('GET', 'https://discord.com/api/v9/users/@me/guilds')
        if response and response.status == 200:
            return data
        return []
    
    def get_channels(self, server_id):
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}/channels')
        if response and response.status == 200:
            return data
        return []
    
    def get_roles(self, server_id):
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}/roles')
        if response and response.status == 200:
            return data
        return []
    
    def get_server_icon(self, server_id):
        try:
            server_info = self.get_server_info(server_id)
            if server_info and server_info.get('icon'):
                icon_hash = server_info['icon']
                icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon_hash}.png?size=128"
                
                req = urllib.request.Request(icon_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                with urllib.request.urlopen(req, context=ssl_context) as icon_response:
                    icon_data = icon_response.read()
                    return base64.b64encode(icon_data).decode()
            return None
        except Exception as e:
            warning(f"Ошибка загрузки аватарки: {e}")
            return None
    
    def delete_channel(self, channel_id):
        response, _ = self.make_request('DELETE', f'https://discord.com/api/v9/channels/{channel_id}')
        return response and response.status == 200
    
    def create_channel(self, server_id, channel_data):
        response, data = self.make_request('POST', f'https://discord.com/api/v9/guilds/{server_id}/channels', channel_data)
        return response and response.status == 201, data
    
    def create_role(self, server_id, role_data):
        response, data = self.make_request('POST', f'https://discord.com/api/v9/guilds/{server_id}/roles', role_data)
        return response and response.status == 200, data
    
    def update_role_positions(self, server_id, position_data):
        response, result = self.make_request('PATCH', f'https://discord.com/api/v9/guilds/{server_id}/roles', position_data)
        return response and response.status == 200
    
    def update_server_info(self, server_id, server_data):
        response, result = self.make_request('PATCH', f'https://discord.com/api/v9/guilds/{server_id}', server_data)
        return response and response.status == 200
    
    def delete_role(self, server_id, role_id):
        try:
            url = f'https://discord.com/api/v9/guilds/{server_id}/roles/{role_id}'
            req = urllib.request.Request(
                url,
                headers=self.headers,
                method='DELETE'
            )
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                if response.status == 204:
                    return True
                else:
                    warning(f"Неожиданный статус код: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            if e.code == 429:
                warning("Rate limit, ждем...")
                time.sleep(2)
                return self.delete_role(server_id, role_id)
            error(f"HTTP Error {e.code} при удалении роли: {e.reason}")
            return False
        except Exception as e:
            error(f"Request Error при удалении роли: {e}")
            return False
    
    def clone_server(self, source_id, target_id):
        header("🚀 ЗАПУСК КЛОНИРОВАНИЯ")
        
        info("Получаем информацию о серверах...")
        source_info = self.get_server_info(source_id)
        if not source_info:
            error("Не удалось получить информацию об исходном сервере!")
            return
        
        server_name = source_info.get('name', 'Unknown Server')
        
        info("Копируем название сервера...")
        name_data = {'name': server_name}
        if self.update_server_info(target_id, name_data):
            success(f"Название скопировано: {server_name}")
        else:
            error("Ошибка копирования названия")
        
        info("Копируем аватарку сервера...")
        server_icon_b64 = self.get_server_icon(source_id)
        if server_icon_b64:
            try:
                icon_data = {'icon': f"data:image/png;base64,{server_icon_b64}"}
                if self.update_server_info(target_id, icon_data):
                    success("Аватарка скопирована!")
                else:
                    error("Ошибка копирования аватарки")
            except Exception as e:
                error(f"Ошибка при обработке аватарки: {e}")
        else:
            warning("У исходного сервера нет аватарки")
        
        info("Анализируем структуру серверов...")
        source_channels = self.get_channels(source_id)
        target_channels = self.get_channels(target_id)
        source_roles = self.get_roles(source_id)
        target_roles = self.get_roles(target_id)
        
        success(f"Исходный сервер: {len(source_channels)} каналов, {len(source_roles)} ролей")
        warning(f"Целевой сервер: {len(target_channels)} каналов, {len(target_roles)} ролей")
        
        header("🗑️  ОЧИСТКА ЦЕЛЕВОГО СЕРВЕРА")
        
        info("Удаляем каналы...")
        channels_deleted = 0
        for channel in target_channels:
            if self.delete_channel(channel['id']):
                success(f"Удален канал: {channel['name']}")
                channels_deleted += 1
            else:
                error(f"Ошибка удаления: {channel['name']}")
            time.sleep(self.rate_limit_delay)
        
        info("Удаляем роли...")
        roles_deleted = 0
        for role in target_roles:
            if not role['managed'] and role['name'] != '@everyone':
                if self.delete_role(target_id, role['id']):
                    success(f"Удалена роль: {role['name']}")
                    roles_deleted += 1
                else:
                    error(f"Ошибка удаления: {role['name']}")
                time.sleep(self.rate_limit_delay)
        
        success(f"Удалено: {channels_deleted} каналов, {roles_deleted} ролей")
        
        header("🎨 СОЗДАНИЕ РОЛЕЙ")
        
        roles_to_create = [role for role in source_roles if not role['managed'] and role['name'] != '@everyone']
        sorted_roles = sorted(roles_to_create, key=lambda x: x['position'], reverse=True)
        
        role_mapping = {}
        role_count = 0
        
        for role in sorted_roles:
            role_data = {
                'name': role['name'],
                'color': role['color'],
                'hoist': role['hoist'],
                'mentionable': role['mentionable'],
                'permissions': str(role['permissions'])
            }
            
            success_create, response_data = self.create_role(target_id, role_data)
            if success_create:
                role_mapping[role['name']] = response_data['id']
                success(f"Создана роль: {role['name']}")
                role_count += 1
            else:
                error(f"Ошибка создания: {role['name']}")
            time.sleep(self.rate_limit_delay)
        
        info("Устанавливаем порядок ролей...")
        if role_mapping:
            position_updates = []
            for source_role in sorted_roles:
                if source_role['name'] in role_mapping:
                    position_updates.append({
                        'id': role_mapping[source_role['name']],
                        'position': source_role['position']
                    })
            
            if position_updates and self.update_role_positions(target_id, position_updates):
                success("Порядок ролей обновлен!")
            else:
                warning("Не удалось обновить порядок ролей")
        else:
            warning("Нет ролей для обновления позиций")
        
        header("🏗️  СОЗДАНИЕ СТРУКТУРЫ КАНАЛОВ")
        
        categories = [ch for ch in source_channels if ch['type'] == 4]
        category_map = {}
        
        info("Создаем категории...")
        for category in categories:
            category_data = {
                'name': category['name'],
                'type': 4,
                'position': category['position']
            }
            
            success_create, data = self.create_channel(target_id, category_data)
            if success_create:
                category_map[category['id']] = data['id']
                success(f"Создана категория: {category['name']}")
            else:
                error(f"Ошибка создания категории: {category['name']}")
            time.sleep(self.rate_limit_delay)
        
        created_count = 0
        channels = [ch for ch in source_channels if ch['type'] != 4]
        
        info("Создаем каналы...")
        for channel in channels:
            channel_data = {
                'name': channel['name'],
                'type': channel['type'],
                'position': channel['position']
            }
            
            if channel.get('parent_id') and channel['parent_id'] in category_map:
                channel_data['parent_id'] = category_map[channel['parent_id']]
            
            success_create, _ = self.create_channel(target_id, channel_data)
            if success_create:
                success(f"Создан канал: {channel['name']}")
                created_count += 1
            else:
                error(f"Ошибка создания: {channel['name']}")
            time.sleep(self.rate_limit_delay)
        
        header("🎉 КЛОНИРОВАНИЕ ЗАВЕРШЕНО")
        success(f"Название сервера: {server_name}")
        success(f"Создано категорий: {len(categories)}")
        success(f"Создано каналов: {created_count}")
        success(f"Создано ролей: {role_count}")
        if server_icon_b64:
            success("Аватарка сервера: Скопирована")
        print(line())

async def check_servers_async(token):
    headers = {'Authorization': token}
    
    async with aiohttp.ClientSession() as session:
        info("Проверяем токен...")
        try:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as r:
                if r.status == 200:
                    user = await r.json()
                    success("ТОКЕН РАБОЧИЙ!")
                    info(f"Пользователь: {user['username']}#{user['discriminator']}")
                    info(f"ID пользователя: {user['id']}")
                    info(f"Email: {user.get('email', 'Скрыт')}")
                    
                    info("Получаем список серверов...")
                    async with session.get('https://discord.com/api/v9/users/@me/guilds', headers=headers) as guilds_r:
                        if guilds_r.status == 200:
                            guilds = await guilds_r.json()
                            success(f"Найдено серверов: {len(guilds)}")
                            
                            header("📋 СПИСОК СЕРВЕРОВ")
                            for i, guild in enumerate(guilds, 1):
                                guild_id = guild['id']
                                guild_name = guild['name']
                                permissions = guild.get('permissions', 0)
                                is_admin = (int(permissions) & 0x8) == 0x8
                                admin_badge = f" {RED}[ADMIN]" if is_admin else ""
                                
                                print(f"{WHITE}{i:2d}. {guild_name}{admin_badge}")
                                print(f"    {CYAN}ID: {WHITE}{guild_id}")
                                if i < len(guilds):
                                    print(f"{BLUE}    {'─' * 40}")
                            
                            print(line())
                            success("Все сервера загружены успешно!")
                                
                        else:
                            error(f"Не удалось получить список серверов: {guilds_r.status}")
                else:
                    error(f"Токен невалидный: {r.status}")
        except aiohttp.ClientConnectionError:
            error("Ошибка подключения к Discord!")
            return
        except asyncio.TimeoutError:
            error("Таймаут подключения!")
            return
        except Exception as e:
            error(f"Неожиданная ошибка: {e}")
            return

def check_servers(token):
    asyncio.run(check_servers_async(token))

def check_server_menu():
    print_banner()
    
    info("Выберите способ ввода токена:")
    info("1. Ввести токен вручную")
    info("2. Использовать токен из файла")
    info("3. Инструкция по получению токена")
    info("4. Назад в главное меню")
    
    choice = input_prompt("Выберите вариант (1/2/3/4): ").strip()
    
    if choice == "4":
        return
    
    token = ""
    
    if choice == "1":
        warning("Внимание: Токен будет виден при вводе!")
        token = input_field("Введите токен")
        
    elif choice == "2":
        try:
            with open("token.txt", "r", encoding="utf-8") as f:
                token = f.read().strip()
            success("Токен успешно загружен из файла token.txt")
        except FileNotFoundError:
            error("Файл token.txt не найден!")
            info("Создайте файл token.txt и поместите в него ваш токен")
            input_prompt("Нажмите Enter для продолжения...")
            check_server_menu()
            return
        except Exception as e:
            error(f"Ошибка при чтении файла: {e}")
            input_prompt("Нажмите Enter для продолжения...")
            check_server_menu()
            return
    
    elif choice == "3":
        header("📖 ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ ТОКЕНА")
        info("1. Откройте Discord в браузере")
        info("2. Нажмите F12 → Вкладка 'Network'")
        info("3. Обновите страницу (F5)")
        info("4. Найдите любой запрос к discord.com")
        info("5. В Headers найдите 'Authorization'")
        info("6. Скопируйте токен (начинается с букв)")
        warning("⚠️  Никому не передавайте ваш токен!")
        input_prompt("Нажмите Enter для возврата...")
        check_server_menu()
        return
    
    else:
        error("Неверный выбор!")
        input_prompt("Нажмите Enter для продолжения...")
        check_server_menu()
        return
    
    if not token:
        error("Токен не может быть пустым!")
        input_prompt("Нажмите Enter для продолжения...")
        check_server_menu()
        return
    
    check_servers(token)
    input_prompt("Нажмите Enter для возврата в меню...")

def main_cloner():
    if not confirm_agreement():
        error("Вы не подтвердили пользовательское соглашение!")
        input_prompt("Нажмите Enter для выхода...")
        return
    
    print_banner()
    
    info("Введите данные для клонирования:")
    
    token = input_field("Токен Discord")
    if not token:
        error("Токен не может быть пустым!")
        input_prompt("Нажмите Enter для продолжения...")
        return
    
    source_id = input_field("ID исходного сервера")
    target_id = input_field("ID целевого сервера")
    
    cloner = AdvancedCloner(token)
    
    info("Проверяем доступ к серверам...")
    servers = cloner.get_servers()
    source_exists = any(s['id'] == source_id for s in servers)
    target_exists = any(s['id'] == target_id for s in servers)
    
    if not source_exists:
        error("Исходный сервер не найден!")
        warning("Убедитесь, что у вас есть доступ к этому серверу")
        input_prompt("Нажмите Enter для продолжения...")
        return
    
    if not target_exists:
        error("Целевой сервер не найден!")
        warning("Убедитесь, что у вас есть доступ к этому серверу")
        input_prompt("Нажмите Enter для продолжения...")
        return
    
    success("Серверы найдены и доступны!")
    
    header("⚠️  ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ")
    error("ВСЕ КАНАЛЫ И РОЛИ НА ЦЕЛЕВОМ СЕРВЕРЕ БУДУТ УДАЛЕНЫ!")
    warning("Будет скопировано: название, аватарка, роли, категории, каналы")
    print(line())
    
    confirm = input_prompt("Начать клонирование? (y/n): ").lower()
    
    if confirm == 'y':
        cloner.clone_server(source_id, target_id)
    else:
        error("Операция отменена пользователем")
    
    input_prompt("Нажмите Enter для возврата в меню...")

def main_menu():
    print_banner()
    
    info("Выберите режим работы:")
    info("1. Клонирование сервера")
    info("2. Проверка серверов (получить ID)")
    info("3. Выход")
    
    choice = input_prompt("Выберите вариант (1/2/3): ").strip()
    
    if choice == "1":
        main_cloner()
        main_menu()
    elif choice == "2":
        check_server_menu()
        main_menu()
    elif choice == "3":
        success("До свидания!")
        return
    else:
        error("Неверный выбор!")
        input_prompt("Нажмите Enter для продолжения...")
        main_menu()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print()
        error("Программа прервана пользователем")
    except Exception as e:
        print()
        error(f"Произошла ошибка: {e}")
    
    input_prompt("Нажмите Enter для выхода...")