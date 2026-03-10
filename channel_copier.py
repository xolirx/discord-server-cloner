import sys
import os
import json
import time
import asyncio
import aiohttp
import ssl
import re
import traceback
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import IntEnum
from functools import lru_cache

if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except:
        pass

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    MAGENTA = Fore.MAGENTA
    RESET = Style.RESET_ALL
except ImportError:
    BLUE = CYAN = WHITE = GREEN = RED = YELLOW = MAGENTA = RESET = ""

VERSION = "6.2.0"
AUTHOR = "xolirx"
TELEGRAM = "@xolirx"
SUPPORT_CHANNEL = "https://t.me/xolirxx"

class ChannelType(IntEnum):
    GUILD_TEXT = 0
    GUILD_VOICE = 2
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    GUILD_STAGE_VOICE = 13
    GUILD_FORUM = 15

    @classmethod
    def is_valid(cls, value: int) -> bool:
        return value in [0, 2, 4, 5, 13, 15]

@dataclass
class RateLimitInfo:
    retry_after: float = 0
    reset_after: float = 0
    limit: int = 0
    remaining: int = 0

class ConsoleUI:
    WIDTH = 65
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def separator():
        return BLUE + "─" * ConsoleUI.WIDTH
    
    @staticmethod
    def header(text: str):
        print(f"\n{BLUE}┌{'─' * (ConsoleUI.WIDTH - 2)}┐")
        print(f"{BLUE}│ {CYAN}{text:^{ConsoleUI.WIDTH - 4}} {BLUE}│")
        print(f"{BLUE}└{'─' * (ConsoleUI.WIDTH - 2)}┘")
    
    @staticmethod
    def title(text: str):
        print(f"\n{BLUE}├{'─' * (ConsoleUI.WIDTH - 2)}┤")
        print(f"{BLUE}│ {CYAN}{text:^{ConsoleUI.WIDTH - 4}} {BLUE}│")
        print(f"{BLUE}├{'─' * (ConsoleUI.WIDTH - 2)}┤")
    
    @staticmethod
    def info(text: str):
        print(f"{CYAN}│ {WHITE}{text}")
    
    @staticmethod
    def success(text: str):
        print(f"{CYAN}│ {GREEN}[+] {WHITE}{text}")
    
    @staticmethod
    def warning(text: str):
        print(f"{CYAN}│ {YELLOW}[!] {WHITE}{text}")
    
    @staticmethod
    def error(text: str):
        print(f"{CYAN}│ {RED}[-] {WHITE}{text}")
    
    @staticmethod
    def progress(text: str):
        print(f"{CYAN}│ {BLUE}[*] {WHITE}{text}")
    
    @staticmethod
    def input_prompt(text: str) -> str:
        print(f"{CYAN}│ {MAGENTA}[?] {WHITE}{text}")
        print(f"{CYAN}│ {MAGENTA}  → {WHITE}", end="")
        return input()
    
    @staticmethod
    def input_field(text: str) -> str:
        print(f"{CYAN}│ {BLUE}[>] {WHITE}{text}:")
        print(f"{CYAN}│ {BLUE}  → {WHITE}", end="")
        return input()
    
    @staticmethod
    def banner():
        ConsoleUI.clear()
        print(f"{BLUE}╔{'═' * (ConsoleUI.WIDTH - 2)}╗")
        print(f"{BLUE}║ {CYAN}{'DISCORD SERVER CLONER':^{ConsoleUI.WIDTH - 4}} {BLUE}║")
        print(f"{BLUE}║ {CYAN}{f'ВЕРСИЯ {VERSION}':^{ConsoleUI.WIDTH - 4}} {BLUE}║")
        print(f"{BLUE}╠{'═' * (ConsoleUI.WIDTH - 2)}╣")
        print(f"{BLUE}║ {WHITE}Автор: {CYAN}{AUTHOR}{' ' * (ConsoleUI.WIDTH - 14 - len(AUTHOR))} {BLUE}║")
        print(f"{BLUE}║ {WHITE}Telegram: {CYAN}{TELEGRAM}{' ' * (ConsoleUI.WIDTH - 17 - len(TELEGRAM))} {BLUE}║")
        print(f"{BLUE}║ {WHITE}Канал: {CYAN}{SUPPORT_CHANNEL}{' ' * (ConsoleUI.WIDTH - 15 - len(SUPPORT_CHANNEL))} {BLUE}║")
        print(f"{BLUE}╚{'═' * (ConsoleUI.WIDTH - 2)}╝")
    
    @staticmethod
    def agreement():
        ConsoleUI.clear()
        print(f"{BLUE}╔{'═' * (ConsoleUI.WIDTH - 2)}╗")
        print(f"{BLUE}║ {RED}{'ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ':^{ConsoleUI.WIDTH - 4}} {BLUE}║")
        print(f"{BLUE}╠{'═' * (ConsoleUI.WIDTH - 2)}╣")
        print(f"{BLUE}║ {WHITE}1. Вы несете ответственность за использование{':^{}} {BLUE}║")
        print(f"{BLUE}║ {WHITE}2. Используйте только на серверах с разрешением{':^{}} {BLUE}║")
        print(f"{BLUE}║ {WHITE}3. Автор не несет ответственности за ваши действия{':^{}} {BLUE}║")
        print(f"{BLUE}║ {WHITE}4. Запрещено нарушение правил Discord{':^{}} {BLUE}║")
        print(f"{BLUE}╚{'═' * (ConsoleUI.WIDTH - 2)}╝")

ui = ConsoleUI()

class Validator:
    TOKEN_PATTERNS = [
        r'^[A-Za-z0-9\.\-_]{59}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
        r'^[A-Za-z0-9\.\-_]{24}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
        r'^mfa\.[A-Za-z0-9\.\-_]{84}$',
        r'^[A-Za-z0-9\.\-_]{70,}$'
    ]
    
    @staticmethod
    def validate_token(token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        token = token.strip().strip('"\' ')
        if len(token) < 59:
            return False
        return any(re.match(pattern, token) for pattern in Validator.TOKEN_PATTERNS)
    
    @staticmethod
    def validate_snowflake(snowflake: str) -> bool:
        if not snowflake or not isinstance(snowflake, str):
            return False
        snowflake = snowflake.strip()
        return snowflake.isdigit() and 17 <= len(snowflake) <= 20
    
    @staticmethod
    def clean_name(name: str, max_len: int = 100) -> str:
        if not name or not isinstance(name, str):
            return "канал"
        cleaned = ''.join(c for c in name if c.isprintable() or c == ' ')
        cleaned = ' '.join(cleaned.split())
        if len(cleaned) > max_len:
            cleaned = cleaned[:max_len-3] + "..."
        return cleaned or "канал"

class RateLimiter:
    def __init__(self):
        self.requests_per_minute = 0
        self.last_request_time = 0
        self.delays = {
            'default': 1.0,
            'channel': 1.5,
            'role': 2.0,
            'bulk': 3.0
        }
    
    def wait(self, operation: str = 'default'):
        delay = self.delays.get(operation, self.delays['default'])
        time.sleep(delay)
    
    def update_from_headers(self, headers: Dict):
        if 'X-RateLimit-Remaining' in headers:
            remaining = int(headers.get('X-RateLimit-Remaining', 0))
            if remaining == 0:
                self.delays['default'] *= 1.5

class RequestManager:
    def __init__(self, token: str):
        self.token = token.strip().strip('"\' ')
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter()
        self.base_url = "https://discord.com/api/v10"
        self.timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.retry_count = 3
        
    async def __aenter__(self):
        headers = {
            'Authorization': self.token,
            'User-Agent': f'DiscordCloner/{VERSION}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.session = aiohttp.ClientSession(headers=headers, timeout=self.timeout)
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Tuple[Optional[Dict], int]:
        url = f"{self.base_url}{endpoint}"
        for attempt in range(self.retry_count):
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    self.rate_limiter.update_from_headers(response.headers)
                    
                    if response.status == 429:
                        retry_after = float(response.headers.get('Retry-After', 2))
                        await asyncio.sleep(retry_after)
                        continue
                    
                    if response.status in [200, 201, 204]:
                        if response.status == 204:
                            return None, response.status
                        return await response.json(), response.status
                    
                    if response.status >= 500 and attempt < self.retry_count - 1:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    
                    error_text = await response.text()
                    return {'error': error_text}, response.status
                    
            except asyncio.TimeoutError:
                if attempt == self.retry_count - 1:
                    return {'error': 'Timeout'}, 408
                await asyncio.sleep(1)
            except aiohttp.ClientError as e:
                if attempt == self.retry_count - 1:
                    return {'error': str(e)}, 500
                await asyncio.sleep(1)
        
        return {'error': 'Max retries exceeded'}, 500
    
    async def get(self, endpoint: str) -> Tuple[Optional[Dict], int]:
        return await self._request('GET', endpoint)
    
    async def post(self, endpoint: str, data: Dict) -> Tuple[Optional[Dict], int]:
        return await self._request('POST', endpoint, json=data)
    
    async def delete(self, endpoint: str) -> Tuple[Optional[Dict], int]:
        return await self._request('DELETE', endpoint)
    
    async def patch(self, endpoint: str, data: Dict) -> Tuple[Optional[Dict], int]:
        return await self._request('PATCH', endpoint, json=data)

class Cache:
    def __init__(self, ttl: int = 300):
        self._cache = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return data
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = (value, time.time())
    
    def clear(self):
        self._cache.clear()

class DiscordCloner:
    def __init__(self, token: str):
        self.token = token
        self.cache = Cache(ttl=60)
        self.stats = {
            'channels_created': 0,
            'roles_created': 0,
            'channels_deleted': 0,
            'roles_deleted': 0,
            'api_calls': 0
        }
    
    async def get_current_user(self, rm: RequestManager) -> Optional[Dict]:
        data, status = await rm.get('/users/@me')
        self.stats['api_calls'] += 1
        return data if status == 200 else None
    
    async def get_user_guilds(self, rm: RequestManager) -> List[Dict]:
        cache_key = 'user_guilds'
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data, status = await rm.get('/users/@me/guilds')
        self.stats['api_calls'] += 1
        
        if status == 200 and isinstance(data, list):
            self.cache.set(cache_key, data)
            return data
        return []
    
    async def get_guild_info(self, rm: RequestManager, guild_id: str) -> Optional[Dict]:
        cache_key = f'guild_{guild_id}'
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data, status = await rm.get(f'/guilds/{guild_id}')
        self.stats['api_calls'] += 1
        
        if status == 200:
            self.cache.set(cache_key, data)
            return data
        return None
    
    async def get_guild_channels(self, rm: RequestManager, guild_id: str) -> List[Dict]:
        cache_key = f'channels_{guild_id}'
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data, status = await rm.get(f'/guilds/{guild_id}/channels')
        self.stats['api_calls'] += 1
        
        if status == 200 and isinstance(data, list):
            self.cache.set(cache_key, data)
            return data
        return []
    
    async def get_guild_roles(self, rm: RequestManager, guild_id: str) -> List[Dict]:
        cache_key = f'roles_{guild_id}'
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        data, status = await rm.get(f'/guilds/{guild_id}/roles')
        self.stats['api_calls'] += 1
        
        if status == 200 and isinstance(data, list):
            self.cache.set(cache_key, data)
            return data
        return []
    
    async def delete_channel(self, rm: RequestManager, channel_id: str) -> bool:
        data, status = await rm.delete(f'/channels/{channel_id}')
        self.stats['api_calls'] += 1
        
        if status in [200, 204]:
            self.stats['channels_deleted'] += 1
            rm.rate_limiter.wait('channel')
            return True
        return False
    
    async def create_channel(self, rm: RequestManager, guild_id: str, channel_data: Dict) -> Optional[Dict]:
        clean_data = {
            'name': Validator.clean_name(channel_data.get('name', 'канал')),
            'type': channel_data.get('type', ChannelType.GUILD_TEXT)
        }
        
        if 'parent_id' in channel_data and channel_data['parent_id']:
            clean_data['parent_id'] = channel_data['parent_id']
        
        if 'position' in channel_data:
            clean_data['position'] = max(0, int(channel_data['position']))
        
        data, status = await rm.post(f'/guilds/{guild_id}/channels', clean_data)
        self.stats['api_calls'] += 1
        
        if status == 201:
            self.stats['channels_created'] += 1
            rm.rate_limiter.wait('channel')
            return data
        return None
    
    async def delete_role(self, rm: RequestManager, guild_id: str, role_id: str) -> bool:
        data, status = await rm.delete(f'/guilds/{guild_id}/roles/{role_id}')
        self.stats['api_calls'] += 1
        
        if status in [200, 204]:
            self.stats['roles_deleted'] += 1
            rm.rate_limiter.wait('role')
            return True
        return False
    
    async def create_role(self, rm: RequestManager, guild_id: str, role_data: Dict) -> Optional[Dict]:
        clean_data = {
            'name': Validator.clean_name(role_data.get('name', 'Новая роль'), 100),
            'color': role_data.get('color', 0),
            'hoist': bool(role_data.get('hoist', False)),
            'mentionable': bool(role_data.get('mentionable', False)),
            'permissions': str(role_data.get('permissions', '0'))
        }
        
        data, status = await rm.post(f'/guilds/{guild_id}/roles', clean_data)
        self.stats['api_calls'] += 1
        
        if status == 200:
            self.stats['roles_created'] += 1
            rm.rate_limiter.wait('role')
            return data
        return None
    
    async def update_guild(self, rm: RequestManager, guild_id: str, data: Dict) -> bool:
        data, status = await rm.patch(f'/guilds/{guild_id}', data)
        self.stats['api_calls'] += 1
        return status == 200
    
    async def clear_guild(self, rm: RequestManager, guild_id: str):
        channels = await self.get_guild_channels(rm, guild_id)
        roles = await self.get_guild_roles(rm, guild_id)
        
        if channels:
            ui.title("ОЧИСТКА КАНАЛОВ")
            for channel in channels:
                name = channel.get('name', 'Без названия')
                if await self.delete_channel(rm, channel['id']):
                    ui.success(f"Удален канал: {name}")
                else:
                    ui.error(f"Не удалось удалить канал: {name}")
        
        if roles:
            ui.title("ОЧИСТКА РОЛЕЙ")
            sorted_roles = sorted(roles, key=lambda x: x.get('position', 0))
            for role in sorted_roles:
                if role.get('name') == '@everyone' or role.get('managed', False):
                    continue
                name = role.get('name', 'Без названия')
                if await self.delete_role(rm, guild_id, role['id']):
                    ui.success(f"Удалена роль: {name}")
                else:
                    ui.error(f"Не удалось удалить роль: {name}")
    
    async def clone_roles(self, rm: RequestManager, source_id: str, target_id: str) -> bool:
        source_roles = await self.get_guild_roles(rm, source_id)
        
        roles_to_create = [
            role for role in source_roles 
            if role.get('name') != '@everyone' and not role.get('managed', False)
        ]
        
        if not roles_to_create:
            ui.info("Нет ролей для клонирования")
            return True
        
        ui.title(f"КЛОНИРОВАНИЕ РОЛЕЙ ({len(roles_to_create)})")
        
        sorted_roles = sorted(roles_to_create, key=lambda x: x.get('position', 0), reverse=True)
        role_mapping = {}
        
        for i, role in enumerate(sorted_roles, 1):
            name = role.get('name', f'Роль {i}')
            ui.progress(f"Создание роли {i}/{len(sorted_roles)}: {name}")
            
            new_role = await self.create_role(rm, target_id, role)
            if new_role and 'id' in new_role:
                role_mapping[role['id']] = new_role['id']
                ui.success(f"Создана роль: {name}")
            else:
                ui.error(f"Ошибка создания роли: {name}")
        
        return len(role_mapping) > 0
    
    async def clone_channels(self, rm: RequestManager, source_id: str, target_id: str) -> bool:
        source_channels = await self.get_guild_channels(rm, source_id)
        
        if not source_channels:
            ui.info("Нет каналов для клонирования")
            return True
        
        categories = [ch for ch in source_channels if ch.get('type') == ChannelType.GUILD_CATEGORY]
        other_channels = [ch for ch in source_channels if ch.get('type') != ChannelType.GUILD_CATEGORY]
        
        ui.title(f"КЛОНИРОВАНИЕ КАНАЛОВ ({len(categories)} категорий, {len(other_channels)} каналов)")
        
        category_map = {}
        
        if categories:
            sorted_categories = sorted(categories, key=lambda x: x.get('position', 0))
            for i, category in enumerate(sorted_categories, 1):
                name = category.get('name', f'Категория {i}')
                ui.progress(f"Создание категории {i}/{len(sorted_categories)}: {name}")
                
                new_category = await self.create_channel(rm, target_id, category)
                if new_category and 'id' in new_category:
                    category_map[category['id']] = new_category['id']
                    ui.success(f"Создана категория: {name}")
                else:
                    ui.error(f"Ошибка создания категории: {name}")
        
        if other_channels:
            sorted_channels = sorted(other_channels, key=lambda x: x.get('position', 0))
            created = 0
            
            for i, channel in enumerate(sorted_channels, 1):
                name = channel.get('name', f'Канал {i}')
                channel_type = channel.get('type', 0)
                
                if not ChannelType.is_valid(channel_type):
                    ui.warning(f"Пропущен канал (неподдерживаемый тип {channel_type}): {name}")
                    continue
                
                if channel.get('parent_id') in category_map:
                    channel['parent_id'] = category_map[channel['parent_id']]
                
                ui.progress(f"Создание канала {i}/{len(sorted_channels)}: {name}")
                
                new_channel = await self.create_channel(rm, target_id, channel)
                if new_channel:
                    created += 1
                    ui.success(f"Создан канал: {name}")
                else:
                    ui.error(f"Ошибка создания канала: {name}")
            
            ui.success(f"Создано каналов: {created}/{len(sorted_channels)}")
        
        return True
    
    async def clone_guild(self, source_id: str, target_id: str) -> bool:
        async with RequestManager(self.token) as rm:
            source_info = await self.get_guild_info(rm, source_id)
            target_info = await self.get_guild_info(rm, target_id)
            
            if not source_info or not target_info:
                ui.error("Не удалось получить информацию о серверах")
                return False
            
            source_name = source_info.get('name', 'Неизвестный сервер')
            target_name = target_info.get('name', 'Неизвестный сервер')
            
            ui.success(f"Исходный сервер: {source_name}")
            ui.success(f"Целевой сервер: {target_name}")
            
            await self.clear_guild(rm, target_id)
            
            if source_info.get('name'):
                ui.progress("Копирование названия сервера...")
                if await self.update_guild(rm, target_id, {'name': source_info['name']}):
                    ui.success("Название скопировано")
            
            await self.clone_roles(rm, source_id, target_id)
            await self.clone_channels(rm, source_id, target_id)
            
            return True

async def check_token_and_servers(token: str):
    token = token.strip().strip('"\' ')
    
    async with RequestManager(token) as rm:
        user = await rm.get('/users/@me')
        
        if not user[0] or user[1] != 200:
            ui.error("Неверный токен или ошибка авторизации")
            return False
        
        user_data = user[0]
        ui.success(f"Токен действителен")
        ui.info(f"Пользователь: {user_data.get('username')}#{user_data.get('discriminator', '0')}")
        ui.info(f"ID: {user_data.get('id')}")
        
        guilds_data = await rm.get('/users/@me/guilds')
        
        if guilds_data[1] == 200 and guilds_data[0]:
            guilds = guilds_data[0]
            ui.title(f"СЕРВЕРЫ ({len(guilds)})")
            
            for i, guild in enumerate(guilds, 1):
                name = guild.get('name', 'Неизвестный сервер')
                guild_id = guild.get('id', 'N/A')
                perms = int(guild.get('permissions', 0))
                is_admin = (perms & 0x8) != 0
                
                admin_mark = "[ADMIN]" if is_admin else ""
                print(f"{CYAN}│ {WHITE}{i:2d}. {name} {GREEN}{admin_mark}")
                print(f"{CYAN}│    ID: {guild_id}")
            
            return True
        else:
            ui.warning("Не удалось получить список серверов")
            return False

def main_menu():
    while True:
        ui.banner()
        ui.title("ГЛАВНОЕ МЕНЮ")
        ui.info("1. Клонирование сервера")
        ui.info("2. Проверка токена и серверов")
        ui.info("3. Информация о программе")
        ui.info("4. Выход")
        
        choice = ui.input_prompt("Выберите вариант (1-4):").strip()
        
        if choice == "1":
            run_cloner()
        elif choice == "2":
            run_token_check()
        elif choice == "3":
            show_info()
        elif choice == "4":
            ui.header("ВЫХОД")
            ui.success("До свидания!")
            break
        else:
            ui.error("Неверный выбор")

def show_info():
    ui.clear()
    ui.header("ИНФОРМАЦИЯ О ПРОГРАММЕ")
    ui.info(f"Версия: {VERSION}")
    ui.info(f"Автор: {AUTHOR}")
    ui.info(f"Telegram: {TELEGRAM}")
    ui.info(f"Канал: {SUPPORT_CHANNEL}")
    ui.info("")
    ui.info("Возможности:")
    ui.info("  • Полное клонирование структуры сервера")
    ui.info("  • Копирование ролей с правами")
    ui.info("  • Копирование категорий и каналов")
    ui.info("  • Копирование названия сервера")
    ui.info("  • Улучшенная обработка ошибок")
    ui.info("  • Оптимизированные задержки запросов")
    ui.input_prompt("Нажмите Enter для возврата")

def run_token_check():
    ui.clear()
    ui.banner()
    ui.title("ПРОВЕРКА ТОКЕНА")
    
    token = ui.input_field("Введите токен Discord").strip()
    
    if not token:
        ui.error("Токен не может быть пустым")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    if not Validator.validate_token(token):
        ui.error("Неверный формат токена")
        ui.info("Уберите кавычки и лишние пробелы")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    asyncio.run(check_token_and_servers(token))
    ui.input_prompt("Нажмите Enter для возврата")

def run_cloner():
    ui.clear()
    ui.agreement()
    
    confirm = ui.input_prompt("Введите 'ПОДТВЕРДИТЬ' для продолжения:").strip().upper()
    if confirm != "ПОДТВЕРДИТЬ":
        ui.header("ОТМЕНА")
        ui.error("Операция отменена")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    ui.clear()
    ui.banner()
    ui.title("ВВОД ДАННЫХ")
    
    token = ui.input_field("Токен Discord").strip()
    if not token:
        ui.error("Токен не может быть пустым")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    token = token.strip().strip('"\' ')
    if not Validator.validate_token(token):
        ui.error("Неверный формат токена")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    source_id = ui.input_field("ID исходного сервера").strip()
    if not Validator.validate_snowflake(source_id):
        ui.error("Неверный ID исходного сервера")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    target_id = ui.input_field("ID целевого сервера").strip()
    if not Validator.validate_snowflake(target_id):
        ui.error("Неверный ID целевого сервера")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    if source_id == target_id:
        ui.error("Серверы не могут быть одинаковыми")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    ui.title("ПОДТВЕРЖДЕНИЕ")
    ui.warning("ВНИМАНИЕ: Все каналы и роли на целевом сервере будут удалены!")
    ui.info("Это действие нельзя отменить!")
    
    final_confirm = ui.input_prompt("Продолжить? (y/N):").strip().lower()
    if final_confirm not in ['y', 'yes', 'да', 'д']:
        ui.header("ОТМЕНА")
        ui.error("Операция отменена")
        ui.input_prompt("Нажмите Enter для возврата")
        return
    
    start_time = time.time()
    
    async def run():
        cloner = DiscordCloner(token)
        result = await cloner.clone_guild(source_id, target_id)
        return result, cloner.stats
    
    try:
        result, stats = asyncio.run(run())
        elapsed = time.time() - start_time
        
        ui.clear()
        if result:
            ui.header("ОПЕРАЦИЯ ЗАВЕРШЕНА")
            ui.success("Клонирование выполнено успешно")
            ui.info(f"Время выполнения: {int(elapsed // 60)} мин {int(elapsed % 60)} сек")
            ui.info(f"Создано каналов: {stats['channels_created']}")
            ui.info(f"Создано ролей: {stats['roles_created']}")
            ui.info(f"API запросов: {stats['api_calls']}")
        else:
            ui.header("ОШИБКА")
            ui.error("Не удалось выполнить клонирование")
        
    except Exception as e:
        ui.error(f"Критическая ошибка: {type(e).__name__}")
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Ошибка: {type(e).__name__}: {e}\n")
            f.write(f"Трассировка:\n{traceback.format_exc()}\n")
    
    ui.input_prompt("Нажмите Enter для возврата")

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Программа прервана{RESET}")
    except Exception as e:
        print(f"\n{RED}Критическая ошибка: {type(e).__name__}: {e}{RESET}")
        with open('error_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Ошибка: {type(e).__name__}: {e}\n")
            f.write(f"Трассировка:\n{traceback.format_exc()}\n")

if __name__ == "__main__":
    main()
