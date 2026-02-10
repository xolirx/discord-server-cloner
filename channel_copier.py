import sys
import os
import urllib.request
import urllib.error
import json
import ssl
import time
import base64
import aiohttp
import asyncio
import re
import traceback
import zlib
import gzip
from typing import Optional, Dict, List, Any, Tuple

if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
except ImportError:
    BLUE = CYAN = WHITE = GREEN = RED = YELLOW = MAGENTA = ""

VERSION = "5.1.0"
AUTHOR = "qtiq0"
DISCORD = "zlafik"
TELEGRAM = "@qtiq0"
SUPPORT_CHANNEL = "@biozlafik"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def разделитель(ширина=65):
    return BLUE + "─" * ширина

def заголовок(текст):
    print(f"\n{BLUE}┌{'─' * 63}┐")
    print(f"{BLUE}│ {CYAN}{текст:^61} {BLUE}│")
    print(f"{BLUE}└{'─' * 63}┘")

def подзаголовок(текст):
    print(f"\n{BLUE}├{'─' * 63}┤")
    print(f"{BLUE}│ {CYAN}{текст:^61} {BLUE}│")
    print(f"{BLUE}├{'─' * 63}┤")

def информация(текст):
    print(f"{CYAN}│ {WHITE}{текст}")

def успех(текст):
    print(f"{CYAN}│ {GREEN}[+] {WHITE}{текст}")

def предупреждение(текст):
    print(f"{CYAN}│ {YELLOW}[!] {WHITE}{текст}")

def ошибка(текст):
    print(f"{CYAN}│ {RED}[-] {WHITE}{текст}")

def процесс(текст):
    print(f"{CYAN}│ {BLUE}[*] {WHITE}{текст}")

def ввод_подсказка(текст):
    print(f"{CYAN}│ {MAGENTA}[?] {WHITE}{текст}")
    print(f"{CYAN}│ {MAGENTA}  → {WHITE}", end="")
    return input()

def ввод_поле(текст):
    print(f"{CYAN}│ {BLUE}[>] {WHITE}{текст}:")
    print(f"{CYAN}│ {BLUE}  → {WHITE}", end="")
    return input()

def печать_баннера():
    clear_screen()
    print(f"{BLUE}╔{'═' * 63}╗")
    print(f"{BLUE}║ {CYAN}{'DISCORD SERVER CLONER':^61} {BLUE}║")
    print(f"{BLUE}║ {CYAN}{f'ВЕРСИЯ {VERSION}':^61} {BLUE}║")
    print(f"{BLUE}╠{'═' * 63}╣")
    print(f"{BLUE}║ {WHITE}Автор: {CYAN}{AUTHOR}{'':^47} {BLUE}║")
    print(f"{BLUE}║ {WHITE}Discord: {CYAN}{DISCORD}{'':^46} {BLUE}║")
    print(f"{BLUE}║ {WHITE}Telegram: {CYAN}{TELEGRAM}{'':^46} {BLUE}║")
    print(f"{BLUE}║ {WHITE}Канал: {CYAN}{SUPPORT_CHANNEL}{'':^46} {BLUE}║")
    print(f"{BLUE}╠{'─' * 63}╣")
    print(f"{BLUE}║ {CYAN}Возможности программы:{'':^38} {BLUE}║")
    print(f"{BLUE}║ {WHITE}• Полное клонирование структуры сервера{'':^22} {BLUE}║")
    print(f"{BLUE}║ {WHITE}• Сохранение ролей, каналов и категорий{'':^23} {BLUE}║")
    print(f"{BLUE}║ {WHITE}• Улучшенная обработка ошибок{'':^31} {BLUE}║")
    print(f"{BLUE}║ {WHITE}• Оптимизированные задержки запросов{'':^26} {BLUE}║")
    print(f"{BLUE}║ {WHITE}• Поддержка последних версий Discord API{'':^20} {BLUE}║")
    print(f"{BLUE}╚{'═' * 63}╝")

def печать_соглашения():
    clear_screen()
    print(f"{BLUE}╔{'═' * 63}╗")
    print(f"{BLUE}║ {CYAN}{'ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ':^61} {BLUE}║")
    print(f"{BLUE}╠{'─' * 63}╣")
    print(f"{BLUE}║ {CYAN}ВНИМАТЕЛЬНО ПРОЧИТАЙТЕ ПЕРЕД ИСПОЛЬЗОВАНИЕМ:{'':^20} {BLUE}║")
    print(f"{BLUE}║ {WHITE}1. Вы несете ответственность за использование программы{'':^8} {BLUE}║")
    print(f"{BLUE}║ {WHITE}2. Используйте только на серверах, где имеете разрешение{'':^6} {BLUE}║")
    print(f"{BLUE}║ {WHITE}3. Автор не несет ответственности за ваши действия{'':^11} {BLUE}║")
    print(f"{BLUE}║ {WHITE}4. Запрещено использование для нарушения правил Discord{'':^5} {BLUE}║")
    print(f"{BLUE}╠{'─' * 63}╣")
    print(f"{BLUE}║ {CYAN}При обнаружении ошибок пишите в Telegram автора:{'':^8} {BLUE}║")
    print(f"{BLUE}║ {CYAN}{TELEGRAM}{'':^61} {BLUE}║")
    print(f"{BLUE}╚{'═' * 63}╝")

def подтвердить_соглашение():
    печать_соглашения()
    подтверждение = ввод_подсказка("Для подтверждения введите: 'ПОДТВЕРДИТЬ'")
    return подтверждение.strip().upper() == "ПОДТВЕРДИТЬ"

class SafeSSLContext:
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
    
    def get_context(self):
        return self.ctx

class DiscordValidator:
    @staticmethod
    def validate_token(token: str) -> bool:
        if not token or not isinstance(token, str):
            return False
        
        token = token.strip()
        if len(token) < 59:
            return False
        
        patterns = [
            r'^[A-Za-z0-9\.\-_]{59}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
            r'^[A-Za-z0-9\.\-_]{24}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
            r'^mfa\.[A-Za-z0-9\.\-_]{84}$',
            r'^[A-Za-z0-9\.\-_]{70,}$'
        ]
        
        return any(re.match(pattern, token) for pattern in patterns)

    @staticmethod
    def validate_snowflake(snowflake: str) -> bool:
        if not snowflake or not isinstance(snowflake, str):
            return False
        
        snowflake = snowflake.strip()
        if not snowflake.isdigit():
            return False
        
        if len(snowflake) < 17 or len(snowflake) > 20:
            return False
        
        try:
            return int(snowflake) > 10000000000000000
        except:
            return False

    @staticmethod
    def clean_channel_name(name: str) -> str:
        if not name or not isinstance(name, str):
            return "канал"
        
        cleaned = ''.join(char for char in name if char.isprintable() or char in ' ')
        cleaned = ' '.join(cleaned.split())
        
        if len(cleaned) > 100:
            cleaned = cleaned[:97] + "..."
        
        cleaned = cleaned.replace('```', '`\u200b`\u200b`')
        return cleaned if cleaned and not cleaned.isspace() else "канал"

    @staticmethod
    def clean_role_name(name: str) -> str:
        cleaned = DiscordValidator.clean_channel_name(name)
        return "Новая роль" if cleaned == "канал" else cleaned

    @staticmethod
    def sanitize_permissions(perms: Any) -> str:
        try:
            if isinstance(perms, str):
                perms_int = int(perms)
            elif isinstance(perms, int):
                perms_int = perms
            else:
                perms_int = 1024
            
            perms_int = perms_int & 0x7FFFFFFFFFFFFFFF
            return str(max(perms_int, 1024))
        except:
            return "1024"

class RequestManager:
    def __init__(self, headers: Dict[str, str]):
        self.headers = headers.copy()
        self.ssl_context = SafeSSLContext()
        self.max_retries = 7
        self.base_delay = 2.0
        self.timeout = 75
        self.request_count = 0
        
        self.headers.update({
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (DiscordCloner/{VERSION})',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDE2Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjQxODQ2LCJuYXRpdmVfYnVpbGRfbnVtYmVyIjozODA1OCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
        })

    def _calculate_delay(self, attempt: int) -> float:
        return self.base_delay + (attempt * 1.2)

    def _handle_rate_limit(self, headers: Dict) -> float:
        retry_after = headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after) + 2.5
            except:
                pass
        
        reset_after = headers.get('X-RateLimit-Reset-After')
        if reset_after:
            try:
                return float(reset_after) + 2.5
            except:
                pass
        
        remaining = headers.get('X-RateLimit-Remaining')
        reset = headers.get('X-RateLimit-Reset')
        
        if remaining == '0' and reset:
            try:
                current_time = time.time()
                reset_time = float(reset)
                delay = max(reset_time - current_time, 0) + 2.5
                return delay
            except:
                pass
        
        return 4.0

    def _prepare_data(self, data: Any) -> Optional[bytes]:
        if data is None:
            return None
        
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            elif isinstance(data, str):
                return data.encode('utf-8')
            elif isinstance(data, bytes):
                return data
            else:
                return str(data).encode('utf-8')
        except Exception as e:
            ошибка(f"Ошибка подготовки данных: {e}")
            return None

    def _decode_response_data(self, response_data: bytes, content_encoding: str = None) -> Any:
        if not response_data:
            return None
        
        try:
            decoded_data = response_data
            
            if content_encoding == 'gzip':
                decoded_data = gzip.decompress(response_data)
            elif content_encoding == 'deflate':
                decoded_data = zlib.decompress(response_data, -zlib.MAX_WBITS)
            
            text = decoded_data.decode('utf-8', errors='ignore')
            if not text.strip():
                return None
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            ошибка(f"Ошибка декодирования JSON: {e}")
            return None
        except Exception as e:
            ошибка(f"Ошибка обработки ответа: {type(e).__name__}: {e}")
            return None

    def request(self, method: str, url: str, data: Any = None) -> Tuple[Optional[Any], Optional[Any]]:
        self.request_count += 1
        
        if self.request_count % 8 == 0:
            информация(f"Выполнено запросов: {self.request_count}")
            time.sleep(1.5)
        
        headers = self.headers.copy()
        
        if data is not None:
            headers['Content-Type'] = 'application/json'
        
        for attempt in range(self.max_retries):
            try:
                текущая_задержка = self._calculate_delay(attempt)
                if attempt > 0:
                    информация(f"Повтор {attempt}/{self.max_retries} через {текущая_задержка:.1f} сек")
                    time.sleep(текущая_задержка)
                
                encoded_data = self._prepare_data(data)
                req = urllib.request.Request(
                    url, 
                    data=encoded_data, 
                    headers=headers, 
                    method=method.upper()
                )
                
                with urllib.request.urlopen(
                    req, 
                    context=self.ssl_context.get_context(), 
                    timeout=self.timeout
                ) as response:
                    статус = response.status
                    response_data = response.read()
                    content_encoding = response.headers.get('Content-Encoding')
                    
                    json_data = self._decode_response_data(response_data, content_encoding)
                    
                    if статус == 429:
                        задержка = self._handle_rate_limit(response.headers)
                        предупреждение(f"Rate limit. Ждем {задержка:.1f} сек...")
                        time.sleep(задержка)
                        continue
                    
                    elif статус == 400:
                        ошибка(f"HTTP 400: Неверный запрос к {url}")
                        
                        if json_data and isinstance(json_data, dict):
                            сообщение = json_data.get('message', '')
                            ошибка(f"Сообщение Discord: {сообщение}")
                        
                        if attempt < self.max_retries - 1:
                            время_ожидания = 7.0 + (attempt * 2.5)
                            предупреждение(f"Повтор через {время_ожидания:.1f} сек...")
                            time.sleep(время_ожидания)
                            continue
                        
                        return response, json_data
                    
                    elif 200 <= статус < 300:
                        return response, json_data
                    
                    else:
                        ошибка(f"HTTP {статус}: {method}")
                        
                        if json_data and isinstance(json_data, dict):
                            ошибка(f"Ответ API: {json_data.get('message', 'Без сообщения')}")
                        
                        if attempt < self.max_retries - 1:
                            time.sleep(self._calculate_delay(attempt))
                            continue
                        
                        return response, json_data
            
            except urllib.error.HTTPError as e:
                статус = e.code
                
                if статус == 429:
                    задержка = self._handle_rate_limit(e.headers)
                    предупреждение(f"Rate limit (HTTPError). Ждем {задержка:.1f} сек...")
                    time.sleep(задержка)
                    continue
                
                elif статус == 400:
                    ошибка(f"HTTP 400: Неверный запрос к {url}")
                    
                    try:
                        error_content = e.read()
                        content_encoding = e.headers.get('Content-Encoding')
                        error_data = self._decode_response_data(error_content, content_encoding)
                        if error_data and isinstance(error_data, dict):
                            ошибка(f"Ошибка Discord: {error_data.get('message', 'Неизвестная ошибка')}")
                    except:
                        pass
                    
                    if attempt < self.max_retries - 1:
                        время_ожидания = 8.0 + (attempt * 3.0)
                        предупреждение(f"Повтор через {время_ожидания:.1f} сек...")
                        time.sleep(время_ожидания)
                        continue
                
                elif статус == 401:
                    ошибка("HTTP 401: Неавторизован. Проверьте токен.")
                    return None, {"error": "Unauthorized", "message": "Invalid token"}
                
                elif статус == 403:
                    ошибка("HTTP 403: Доступ запрещен. Недостаточно прав.")
                    return None, {"error": "Forbidden", "message": "Insufficient permissions"}
                
                elif статус == 404:
                    ошибка(f"HTTP 404: Ресурс не найден - {url}")
                    return None, {"error": "Not Found"}
                
                else:
                    ошибка(f"HTTP {статус}: {e.reason} - {url}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self._calculate_delay(attempt))
                        continue
                
                try:
                    error_content = e.read()
                    content_encoding = e.headers.get('Content-Encoding')
                    json_data = self._decode_response_data(error_content, content_encoding)
                    return e, json_data
                except:
                    return e, None
            
            except urllib.error.URLError as e:
                ошибка(f"Ошибка сети: {e.reason}")
                время_ожидания = 4.0 + (attempt * 1.5)
                предупреждение(f"Повтор через {время_ожидания:.1f} сек...")
                time.sleep(время_ожидания)
            
            except ssl.SSLError as e:
                ошибка(f"Ошибка SSL: {e}")
                время_ожидания = 2.5 + attempt
                предупреждение(f"Повтор через {время_ожидания:.1f} сек...")
                time.sleep(время_ожидания)
            
            except Exception as e:
                ошибка(f"Неожиданная ошибка в запросе: {type(e).__name__}: {e}")
                
                if attempt < self.max_retries - 1:
                    время_ожидания = 3.5 + (attempt * 1.5)
                    предупреждение(f"Повтор через {время_ожидания:.1f} сек...")
                    time.sleep(время_ожидания)
                else:
                    информация(f"Если ошибка повторяется, напишите автору: {TELEGRAM}")
        
        ошибка(f"Не удалось после {self.max_retries} попыток: {method} {url}")
        информация(f"Проверьте соединение с интернетом")
        информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
        return None, None

    def get(self, url: str) -> Tuple[Optional[Any], Optional[Any]]:
        return self.request('GET', url)

    def post(self, url: str, data: Any = None) -> Tuple[Optional[Any], Optional[Any]]:
        return self.request('POST', url, data)

    def delete(self, url: str) -> Tuple[Optional[Any], Optional[Any]]:
        return self.request('DELETE', url)

    def patch(self, url: str, data: Any = None) -> Tuple[Optional[Any], Optional[Any]]:
        return self.request('PATCH', url, data)

class AdvancedCloner:
    def __init__(self, token: str):
        if not DiscordValidator.validate_token(token):
            raise ValueError("Неверный формат токена Discord")
        
        self.token = token
        self.validator = DiscordValidator()
        
        self.headers = {
            'Authorization': token,
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (DiscordCloner/{VERSION})',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Debug-Options': 'bugReporterEnabled',
            'X-Discord-Locale': 'en-US',
            'X-Super-Properties': 'eyJvsiOiJXaW5kb3dzIiwiYnJvd3NlciI6IkRpc2NvcmQgQ2xpZW50IiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X3ZlcnNpb24iOiIxLjAuOTAxNiIsIm9zX3ZlcnNpb24iOiIxMC4wLjIyNjIxIiwib3NfYXJjaCI6Ing2NCIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImNsaWVudF9idWlsZF9udW1iZXIiOjI0MTg0NiwibmF0aXZlX2J1aWxkX251bWJlciI6MzgwNTgsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9'
        }
        
        self.request_manager = RequestManager(self.headers)
        self.channel_delay = 2.0
        self.role_delay = 2.5
        self.bulk_delay = 4.0
        self.cache = {}
        self.cache_expiry = {}

    def _check_response(self, response, operation: str = "") -> bool:
        if response is None:
            ошибка(f"Нет ответа для операции: {operation}")
            return False
        
        if hasattr(response, 'status'):
            статус = response.status
            if 200 <= статус < 300:
                return True
            else:
                ошибка(f"Статус {статус} для операции: {operation}")
                return False
        
        return False

    def _get_cached_data(self, key: str, max_age: int = 240) -> Optional[Any]:
        if key in self.cache:
            if key in self.cache_expiry:
                if time.time() < self.cache_expiry[key]:
                    return self.cache[key]
            else:
                return self.cache[key]
        return None

    def _set_cached_data(self, key: str, data: Any, max_age: int = 240):
        self.cache[key] = data
        self.cache_expiry[key] = time.time() + max_age

    def get_server_info(self, server_id: str) -> Optional[Dict]:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return None
        
        cache_key = f"server_{server_id}"
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached
        
        url = f'https://discord.com/api/v10/guilds/{server_id}'
        response, data = self.request_manager.get(url)
        
        if response and self._check_response(response, "get_server_info"):
            if isinstance(data, dict):
                self._set_cached_data(cache_key, data)
                return data
            else:
                ошибка(f"Неверные данные ответа для сервера {server_id}")
        
        return None

    def get_servers(self) -> List[Dict]:
        url = 'https://discord.com/api/v10/users/@me/guilds'
        response, data = self.request_manager.get(url)
        
        if response and self._check_response(response, "get_servers"):
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'message' in data:
                    ошибка(f"Ошибка Discord API: {data.get('message', 'Неизвестная ошибка')}")
                else:
                    ошибка(f"Неверный формат ответа Discord API: dict без message")
            else:
                ошибка(f"Неверный формат ответа от Discord API: {type(data)}")
        
        return []

    def get_channels(self, server_id: str) -> List[Dict]:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return []
        
        cache_key = f"channels_{server_id}"
        cached = self._get_cached_data(cache_key, 150)
        if cached:
            return cached
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/channels'
        response, data = self.request_manager.get(url)
        
        if self._check_response(response, "get_channels"):
            if isinstance(data, list):
                self._set_cached_data(cache_key, data, 150)
                return data
            else:
                ошибка(f"Неверный формат данных каналов: {type(data)}")
        
        return []

    def get_roles(self, server_id: str) -> List[Dict]:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return []
        
        cache_key = f"roles_{server_id}"
        cached = self._get_cached_data(cache_key, 150)
        if cached:
            return cached
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/roles'
        response, data = self.request_manager.get(url)
        
        if self._check_response(response, "get_roles"):
            if isinstance(data, list):
                self._set_cached_data(cache_key, data, 150)
                return data
            else:
                ошибка(f"Неверный формат данных ролей: {type(data)}")
        
        return []

    def get_server_icon(self, server_id: str) -> Optional[str]:
        try:
            server_info = self.get_server_info(server_id)
            if not server_info or not server_info.get('icon'):
                return None
            
            icon_hash = server_info['icon']
            
            for size in [512, 256, 128, 64]:
                try:
                    icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon_hash}.png?size={size}"
                    
                    req = urllib.request.Request(icon_url, headers={
                        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (DiscordCloner/{VERSION})'
                    })
                    
                    with urllib.request.urlopen(req, timeout=35) as response:
                        if response.status == 200:
                            icon_data = response.read()
                            return base64.b64encode(icon_data).decode('utf-8')
                except Exception:
                    continue
            
            return None
        except Exception as e:
            предупреждение(f"Ошибка загрузки иконки сервера: {e}")
            return None

    def delete_channel(self, channel_id: str, channel_name: str = "Неизвестно") -> bool:
        if not self.validator.validate_snowflake(channel_id):
            ошибка(f"Неверный ID канала: {channel_id}")
            return False
        
        url = f'https://discord.com/api/v10/channels/{channel_id}'
        response, _ = self.request_manager.delete(url)
        
        if self._check_response(response, f"delete_channel ({channel_name})"):
            успех(f"Удален канал: {channel_name}")
            time.sleep(self.channel_delay * 0.6)
            return True
        
        return False

    def create_channel(self, server_id: str, channel_data: Dict) -> Tuple[bool, Optional[Dict]]:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return False, None
        
        sanitized_data = self._sanitize_channel_data(channel_data)
        if not sanitized_data:
            return False, None
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/channels'
        response, data = self.request_manager.post(url, sanitized_data)
        
        if self._check_response(response, "create_channel"):
            time.sleep(self.channel_delay)
            return True, data if isinstance(data, dict) else None
        
        return False, None

    def _sanitize_channel_data(self, channel_data: Dict) -> Optional[Dict]:
        if not isinstance(channel_data, dict):
            return None
        
        sanitized = channel_data.copy()
        
        if 'name' not in sanitized:
            sanitized['name'] = "канал"
        
        if 'type' not in sanitized:
            sanitized['type'] = 0
        
        sanitized['name'] = self.validator.clean_channel_name(sanitized['name'])
        
        valid_types = [0, 2, 4, 5, 13, 15]
        if sanitized['type'] not in valid_types:
            предупреждение(f"Неверный тип канала {sanitized['type']}, используем 0 (текстовый)")
            sanitized['type'] = 0
        
        if 'parent_id' in sanitized:
            parent_id = sanitized['parent_id']
            if parent_id and not self.validator.validate_snowflake(str(parent_id)):
                предупреждение(f"Неверный parent_id: {parent_id}, удаляем")
                del sanitized['parent_id']
        
        if 'position' in sanitized:
            try:
                sanitized['position'] = max(0, int(sanitized['position']))
            except:
                sanitized['position'] = 0
        
        if 'rate_limit_per_user' in sanitized:
            try:
                limit = int(sanitized['rate_limit_per_user'])
                sanitized['rate_limit_per_user'] = max(0, min(21600, limit))
            except:
                del sanitized['rate_limit_per_user']
        
        return sanitized

    def create_role(self, server_id: str, role_data: Dict) -> Tuple[bool, Optional[Dict]]:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return False, None
        
        sanitized_data = self._sanitize_role_data(role_data)
        if not sanitized_data:
            return False, None
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/roles'
        response, data = self.request_manager.post(url, sanitized_data)
        
        if self._check_response(response, "create_role"):
            time.sleep(self.role_delay)
            return True, data if isinstance(data, dict) else None
        
        return False, None

    def _sanitize_role_data(self, role_data: Dict) -> Optional[Dict]:
        if not isinstance(role_data, dict):
            return None
        
        sanitized = role_data.copy()
        
        if 'name' not in sanitized:
            sanitized['name'] = "Новая роль"
        
        sanitized['name'] = self.validator.clean_role_name(sanitized['name'])
        
        if 'color' not in sanitized:
            sanitized['color'] = 0
        else:
            try:
                color = int(sanitized['color'])
                sanitized['color'] = max(0, min(0xFFFFFF, color))
            except:
                sanitized['color'] = 0
        
        sanitized['permissions'] = self.validator.sanitize_permissions(
            sanitized.get('permissions', '0')
        )
        
        for field in ['hoist', 'mentionable']:
            if field in sanitized:
                sanitized[field] = bool(sanitized[field])
            else:
                sanitized[field] = False
        
        return sanitized

    def update_role_positions(self, server_id: str, position_data: List[Dict]) -> bool:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return False
        
        if not isinstance(position_data, list) or not position_data:
            предупреждение("Нет данных о позициях")
            return True
        
        validated = []
        for item in position_data:
            if not isinstance(item, dict):
                continue
            
            if 'id' not in item or 'position' not in item:
                continue
            
            if not self.validator.validate_snowflake(str(item['id'])):
                предупреждение(f"Неверный ID роли в данных позиций: {item['id']}")
                continue
            
            try:
                position = int(item['position'])
                if position < 0:
                    предупреждение(f"Неверная позиция: {position}")
                    continue
            except:
                предупреждение(f"Неверное значение позиции: {item['position']}")
                continue
            
            validated.append({
                'id': str(item['id']),
                'position': position
            })
        
        if not validated:
            предупреждение("Нет валидных данных о позициях после проверки")
            return True
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/roles'
        response, _ = self.request_manager.patch(url, validated)
        
        if self._check_response(response, "update_role_positions"):
            time.sleep(self.bulk_delay)
            return True
        
        return False

    def update_server_info(self, server_id: str, server_data: Dict) -> bool:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return False
        
        url = f'https://discord.com/api/v10/guilds/{server_id}'
        response, _ = self.request_manager.patch(url, server_data)
        return self._check_response(response, "update_server_info")

    def delete_role(self, server_id: str, role_id: str, role_name: str = "Неизвестно") -> bool:
        if not self.validator.validate_snowflake(server_id):
            ошибка(f"Неверный ID сервера: {server_id}")
            return False
        
        if not self.validator.validate_snowflake(role_id):
            ошибка(f"Неверный ID роли: {role_id}")
            return False
        
        url = f'https://discord.com/api/v10/guilds/{server_id}/roles/{role_id}'
        response, _ = self.request_manager.delete(url)
        
        if self._check_response(response, f"delete_role ({role_name})"):
            успех(f"Удалена роль: {role_name}")
            time.sleep(self.role_delay * 0.6)
            return True
        
        return False

    def clone_server(self, source_id: str, target_id: str) -> bool:
        try:
            clear_screen()
            заголовок("ЗАПУСК КЛОНИРОВАНИЯ")
            print(f"{BLUE}│")
            
            процесс("Получаем информацию о серверах...")
            
            source_info = self.get_server_info(source_id)
            if not source_info:
                ошибка("Не удалось получить информацию об исходном сервере")
                информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
                return False
            
            target_info = self.get_server_info(target_id)
            if not target_info:
                ошибка("Не удалось получить информацию о целевом сервере")
                информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
                return False
            
            source_name = source_info.get('name', 'Неизвестный сервер')
            target_name = target_info.get('name', 'Неизвестный сервер')
            
            успех(f"Исходный сервер: {CYAN}{source_name}{WHITE}")
            успех(f"Целевой сервер: {CYAN}{target_name}{WHITE}")
            
            print(f"{BLUE}│")
            процесс("Копируем название сервера...")
            
            name_data = {'name': source_name}
            if self.update_server_info(target_id, name_data):
                успех(f"Название скопировано: {CYAN}{source_name}{WHITE}")
            else:
                предупреждение("Не удалось скопировать название")
            
            print(f"{BLUE}│")
            процесс("Копируем иконку сервера...")
            
            icon_b64 = self.get_server_icon(source_id)
            if icon_b64:
                try:
                    icon_data = {'icon': f"data:image/png;base64,{icon_b64}"}
                    if self.update_server_info(target_id, icon_data):
                        успех("Иконка сервера скопирована")
                    else:
                        предупреждение("Не удалось скопировать иконку")
                except Exception as e:
                    предупреждение(f"Ошибка при обработке иконки: {e}")
            else:
                информация("У сервера нет иконки или не удалось ее загрузить")
            
            print(f"{BLUE}│")
            процесс("Анализируем структуры серверов...")
            
            source_channels = self.get_channels(source_id)
            target_channels = self.get_channels(target_id)
            source_roles = self.get_roles(source_id)
            target_roles = self.get_roles(target_id)
            
            успех(f"Исходный сервер: {GREEN}{len(source_channels)}{WHITE} каналов, {GREEN}{len(source_roles)}{WHITE} ролей")
            предупреждение(f"Целевой сервер: {YELLOW}{len(target_channels)}{WHITE} каналов, {YELLOW}{len(target_roles)}{WHITE} ролей")
            
            print(f"{BLUE}│")
            
            if not self._clean_target_server(target_id, target_channels, target_roles):
                ошибка("Не удалось очистить целевой сервер")
                информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
                return False
            
            if not self._clone_roles(source_roles, target_id):
                ошибка("Не удалось клонировать роли")
                информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
                return False
            
            if not self._clone_channels(source_channels, target_id):
                ошибка("Не удалось клонировать каналы")
                информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
                return False
            
            clear_screen()
            заголовок("КЛОНИРОВАНИЕ ЗАВЕРШЕНО")
            print(f"{BLUE}│")
            успех(f"Сервер {CYAN}'{source_name}'{WHITE} успешно клонирован в {CYAN}'{target_name}'{WHITE}")
            успех("Все структуры созданы в правильном порядке")
            print(f"{BLUE}│")
            успех("Перезайдите на сервер, чтобы увидеть все изменения")
            print(f"\n{BLUE}└{'─' * 63}┘")
            return True
        
        except Exception as e:
            ошибка(f"Критическая ошибка при клонировании: {e}")
            информация(f"Если ошибка повторяется, напишите автору: {TELEGRAM}")
            
            with open("error_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Clone Error: {str(e)}\n")
                traceback.print_exc(file=f)
            
            return False

    def _clean_target_server(self, target_id: str, channels: List[Dict], roles: List[Dict]) -> bool:
        подзаголовок("ОЧИСТКА ЦЕЛЕВОГО СЕРВЕРА")
        print(f"{BLUE}│")
        
        if channels:
            процесс(f"Удаляем {YELLOW}{len(channels)}{WHITE} каналов...")
            deleted = 0
            
            for channel in channels:
                channel_name = channel.get('name', 'Без названия')
                if self.delete_channel(channel['id'], channel_name):
                    deleted += 1
                    if deleted % 6 == 0:
                        процесс(f"Прогресс: {GREEN}{deleted}{WHITE}/{YELLOW}{len(channels)}{WHITE} каналов")
                else:
                    ошибка(f"Не удалось удалить канал: {channel_name}")
            
            успех(f"Удалено каналов: {GREEN}{deleted}{WHITE}/{YELLOW}{len(channels)}{WHITE}")
        
        time.sleep(self.bulk_delay * 1.3)
        print(f"{BLUE}│")
        
        if roles:
            процесс(f"Удаляем {YELLOW}{len(roles)}{WHITE} ролей...")
            deleted = 0
            sorted_roles = sorted(roles, key=lambda x: x.get('position', 0))
            
            for role in sorted_roles:
                if role.get('name') == '@everyone' or role.get('managed', False):
                    continue
                
                role_name = role.get('name', 'Без названия')
                if self.delete_role(target_id, role['id'], role_name):
                    deleted += 1
                    if deleted % 4 == 0:
                        процесс(f"Прогресс: {GREEN}{deleted}{WHITE} ролей")
                else:
                    ошибка(f"Не удалось удалить роль: {role_name}")
            
            успех(f"Удалено ролей: {GREEN}{deleted}{WHITE}")
        
        time.sleep(self.bulk_delay * 1.7)
        print(f"\n{BLUE}└{'─' * 63}┘")
        return True

    def _clone_roles(self, source_roles: List[Dict], target_id: str) -> bool:
        заголовок("КЛОНИРОВАНИЕ РОЛЕЙ")
        print(f"{BLUE}│")
        
        roles_to_create = []
        for role in source_roles:
            if role.get('name') == '@everyone' or role.get('managed', False):
                continue
            roles_to_create.append(role)
        
        if not roles_to_create:
            информация("Нет ролей для клонирования")
            print(f"\n{BLUE}└{'─' * 63}┘")
            return True
        
        успех(f"Будет создано: {CYAN}{len(roles_to_create)}{WHITE} ролей")
        print(f"{BLUE}│")
        
        sorted_roles = sorted(roles_to_create, key=lambda x: x.get('position', 0), reverse=True)
        role_mapping = {}
        created = 0
        
        процесс("Создаем роли...")
        
        for i, role in enumerate(sorted_roles, 1):
            role_name = role.get('name', f'Роль {i}')
            role_data = {
                'name': role_name,
                'color': role.get('color', 0),
                'hoist': role.get('hoist', False),
                'mentionable': role.get('mentionable', False),
                'permissions': role.get('permissions', '0')
            }
            
            success_create, response_data = self.create_role(target_id, role_data)
            
            if success_create and isinstance(response_data, dict):
                new_role_id = response_data.get('id')
                if new_role_id:
                    role_mapping[role['id']] = new_role_id
                    created += 1
                    успех(f"Создана роль: {CYAN}{role_name}{WHITE} ({GREEN}{i}{WHITE}/{YELLOW}{len(sorted_roles)}{WHITE})")
                else:
                    ошибка(f"Не удалось получить ID созданной роли: {role_name}")
            else:
                ошибка(f"Ошибка создания роли: {role_name}")
            
            if i % 4 == 0 or i == len(sorted_roles):
                процесс(f"Прогресс: {GREEN}{i}{WHITE}/{YELLOW}{len(sorted_roles)}{WHITE} ролей")
        
        print(f"{BLUE}│")
        
        if role_mapping:
            процесс("Обновляем порядок ролей...")
            position_updates = []
            
            for source_role in sorted_roles:
                source_id = source_role['id']
                if source_id in role_mapping:
                    position_updates.append({
                        'id': role_mapping[source_id],
                        'position': source_role.get('position', 0)
                    })
            
            if position_updates:
                self.update_role_positions(target_id, position_updates)
        
        успех(f"Создано ролей: {GREEN}{created}{WHITE}/{YELLOW}{len(sorted_roles)}{WHITE}")
        print(f"\n{BLUE}└{'─' * 63}┘")
        return created > 0

    def _clone_channels(self, source_channels: List[Dict], target_id: str) -> bool:
        заголовок("КЛОНИРОВАНИЕ КАНАЛОВ")
        print(f"{BLUE}│")
        
        if not source_channels:
            информация("Нет каналов для клонирования")
            print(f"\n{BLUE}└{'─' * 63}┘")
            return True
        
        categories = [ch for ch in source_channels if ch.get('type') == 4]
        channels = [ch for ch in source_channels if ch.get('type') != 4]
        
        успех(f"Будет создано: {CYAN}{len(categories)}{WHITE} категорий и {CYAN}{len(channels)}{WHITE} каналов")
        print(f"{BLUE}│")
        
        category_map = {}
        
        if categories:
            процесс("Создаем категории...")
            sorted_categories = sorted(categories, key=lambda x: x.get('position', 0))
            
            for i, category in enumerate(sorted_categories, 1):
                category_name = category.get('name', f'Категория {i}')
                category_data = {
                    'name': category_name,
                    'type': 4,
                    'position': category.get('position', 0)
                }
                
                success_create, response_data = self.create_channel(target_id, category_data)
                
                if success_create and isinstance(response_data, dict):
                    new_id = response_data.get('id')
                    if new_id:
                        category_map[category['id']] = new_id
                        успех(f"Создана категория: {CYAN}{category_name}{WHITE} ({GREEN}{i}{WHITE}/{YELLOW}{len(sorted_categories)}{WHITE})")
                    else:
                        ошибка(f"Не удалось получить ID категории: {category_name}")
                else:
                    ошибка(f"Ошибка создания категории: {category_name}")
                
                if i % 3 == 0 or i == len(sorted_categories):
                    процесс(f"Прогресс категорий: {GREEN}{i}{WHITE}/{YELLOW}{len(sorted_categories)}{WHITE}")
        
        time.sleep(self.bulk_delay * 0.8)
        print(f"{BLUE}│")
        
        if channels:
            процесс("Создаем каналы...")
            sorted_channels = sorted(channels, key=lambda x: x.get('position', 0))
            created = 0
            
            for i, channel in enumerate(sorted_channels, 1):
                channel_name = channel.get('name', f'Канал {i}')
                channel_type = channel.get('type', 0)
                
                valid_types = [0, 2, 5, 13, 15]
                if channel_type not in valid_types:
                    предупреждение(f"Пропускаем тип {channel_type}: {channel_name}")
                    continue
                
                channel_data = {
                    'name': channel_name,
                    'type': channel_type,
                    'position': channel.get('position', 0)
                }
                
                parent_id = channel.get('parent_id')
                if parent_id and parent_id in category_map:
                    channel_data['parent_id'] = category_map[parent_id]
                
                success_create, _ = self.create_channel(target_id, channel_data)
                
                if success_create:
                    created += 1
                    успех(f"Создан канал: {CYAN}{channel_name}{WHITE} ({GREEN}{i}{WHITE}/{YELLOW}{len(sorted_channels)}{WHITE})")
                else:
                    ошибка(f"Ошибка создания канала: {channel_name}")
                
                if i % 10 == 0 or i == len(sorted_channels):
                    процесс(f"Прогресс каналов: {GREEN}{i}{WHITE}/{YELLOW}{len(sorted_channels)}{WHITE}")
            
            успех(f"Создано каналов: {GREEN}{created}{WHITE}/{YELLOW}{len(sorted_channels)}{WHITE}")
        
        print(f"\n{BLUE}└{'─' * 63}┘")
        return True

async def check_servers_async(token: str):
    headers = {
        'Authorization': token,
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (DiscordCloner/{VERSION})',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'X-Debug-Options': 'bugReporterEnabled',
        'X-Discord-Locale': 'en-US',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDE2Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjQxODQ2LCJuYXRpdmVfYnVpbGRfbnVtYmVyIjozODA1OCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0='
    }
    
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=35)) as session:
        try:
            clear_screen()
            заголовок("ПРОВЕРКА СЕРВЕРОВ")
            print(f"{BLUE}│")
            
            процесс("Проверяем токен...")
            
            async with session.get('https://discord.com/api/v10/users/@me', timeout=35) as response:
                if response.status == 200:
                    user_data = await response.json()
                    username = user_data.get('username', 'N/A')
                    user_id = user_data.get('id', 'N/A')
                    
                    успех("ТОКЕН РАБОЧИЙ")
                    информация(f"Пользователь: {CYAN}{username}{WHITE}")
                    информация(f"ID: {CYAN}{user_id}{WHITE}")
                    
                    print(f"{BLUE}│")
                    процесс("Получаем список серверов...")
                    
                    async with session.get('https://discord.com/api/v10/users/@me/guilds', timeout=35) as guilds_response:
                        if guilds_response.status == 200:
                            guilds_data = await guilds_response.read()
                            try:
                                guilds = json.loads(guilds_data.decode('utf-8'))
                            except json.JSONDecodeError as e:
                                ошибка(f"Ошибка декодирования JSON: {e}")
                                return
                            
                            успех(f"Найдено серверов: {CYAN}{len(guilds)}{WHITE}")
                            
                            if guilds:
                                подзаголовок("СПИСОК СЕРВЕРОВ")
                                
                                for i, guild in enumerate(guilds, 1):
                                    guild_id = guild.get('id', 'N/A')
                                    guild_name = guild.get('name', 'Неизвестный сервер')
                                    permissions = int(guild.get('permissions', 0))
                                    is_admin = (permissions & 0x8) != 0
                                    is_owner = guild.get('owner', False)
                                    
                                    admin_badge = f" {GREEN}[ADMIN]{WHITE}" if is_admin else ""
                                    owner_badge = f" {MAGENTA}[ВЛАДЕЛЕЦ]{WHITE}" if is_owner else ""
                                    icon = f" {CYAN}[ICON]{WHITE}" if guild.get('icon') else ""
                                    
                                    print(f"{BLUE}│ {WHITE}{i:3d}. {CYAN}{guild_name}{WHITE}{admin_badge}{owner_badge}{icon}")
                                    print(f"{BLUE}│     {BLUE}ID: {CYAN}{guild_id}{WHITE}")
                                    
                                    if i < len(guilds):
                                        print(f"{BLUE}│     {BLUE}{'─' * 55}")
                                
                                print(f"{BLUE}│")
                                успех("Все сервера успешно загружены")
                                информация("Скопируйте ID нужного сервера для клонирования")
                            else:
                                предупреждение("Вы не состоите ни в одном сервере")
                        else:
                            ошибка(f"Не удалось получить серверы: {guilds_response.status}")
                else:
                    ошибка(f"Токен невалидный: {response.status}")
        
        except aiohttp.ClientConnectionError:
            ошибка("Ошибка подключения к Discord")
            информация("Проверьте интернет соединение")
        except asyncio.TimeoutError:
            ошибка("Таймаут подключения")
            информация("Увеличено время ожидания ответа")
        except aiohttp.ClientResponseError as e:
            ошибка(f"Ошибка ответа: {e.status} - {e.message}")
        except Exception as e:
            ошибка(f"Неожиданная ошибка: {type(e).__name__}: {e}")
            информация(f"Если ошибка повторяется, напишите автору: {TELEGRAM}")
        
        print(f"\n{BLUE}└{'─' * 63}┘")

def check_servers(token: str):
    asyncio.run(check_servers_async(token))

def check_server_menu():
    clear_screen()
    печать_баннера()
    подзаголовок("ВЫБОР СПОСОБА ВВОДА ТОКЕНА")
    print(f"{BLUE}│")
    информация("1. Ввести токен вручную")
    информация("2. Инструкция по получению токена")
    информация("3. Назад в главное меню")
    print(f"{BLUE}│")
    
    choice = ввод_подсказка("Выберите вариант (1/2/3):").strip()
    
    if choice == "3":
        return
    
    token = ""
    
    if choice == "1":
        предупреждение("Внимание: Токен будет виден при вводе")
        token = ввод_поле("Введите токен Discord").strip()
    
    elif choice == "2":
        clear_screen()
        заголовок("ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ ТОКЕНА")
        print(f"{BLUE}│")
        информация("1. Откройте Discord в браузере")
        информация("2. Нажмите F12 (Инструменты разработчика)")
        информация("3. Перейдите на вкладку 'Console'")
        информация("4. Введите команду: localStorage.token")
        информация("5. Скопируйте токен (длинная строка в кавычках)")
        print(f"{BLUE}│")
        предупреждение("ВАЖНО: Никому не передавайте ваш токен")
        предупреждение("Токен дает полный доступ к вашему аккаунту")
        информация(f"При проблемах пишите автору: {TELEGRAM}")
        print(f"\n{BLUE}└{'─' * 63}┘")
        ввод_подсказка("Нажмите Enter для возврата")
        check_server_menu()
        return
    
    else:
        ошибка("Неверный выбор")
        ввод_подсказка("Нажмите Enter для продолжения")
        check_server_menu()
        return
    
    if not token:
        ошибка("Токен не может быть пустым")
        ввод_подсказка("Нажмите Enter для продолжения")
        check_server_menu()
        return
    
    if not DiscordValidator.validate_token(token):
        ошибка("Неверный формат токена")
        информация("Токен должен быть длинной строкой (59+ символов)")
        ввод_подсказка("Нажмите Enter для продолжения")
        check_server_menu()
        return
    
    check_servers(token)
    ввод_подсказка("Нажмите Enter для возврата в меню")

def main_cloner():
    if not подтвердить_соглашение():
        clear_screen()
        заголовок("ОТМЕНА")
        print(f"{BLUE}│")
        ошибка("Вы не подтвердили пользовательское соглашение")
        print(f"\n{BLUE}└{'─' * 63}┘")
        ввод_подсказка("Нажмите Enter для выхода")
        return
    
    clear_screen()
    печать_баннера()
    подзаголовок("ВВОД ДАННЫХ ДЛЯ КЛОНИРОВАНИЯ")
    print(f"{BLUE}│")
    
    token = ввод_поле("Токен Discord").strip()
    if not token:
        ошибка("Токен не может быть пустым")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    if not DiscordValidator.validate_token(token):
        ошибка("Неверный формат токена")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    source_id = ввод_поле("ID исходного сервера").strip()
    if not source_id or not DiscordValidator.validate_snowflake(source_id):
        ошибка("Неверный ID исходного сервера")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    target_id = ввод_поле("ID целевого сервера").strip()
    if not target_id or not DiscordValidator.validate_snowflake(target_id):
        ошибка("Неверный ID целевого сервера")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    if source_id == target_id:
        ошибка("Исходный и целевой сервер не могут быть одинаковыми")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    try:
        cloner = AdvancedCloner(token)
    except ValueError as e:
        ошибка(f"Ошибка инициализации: {e}")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    except Exception as e:
        ошибка(f"Неожиданная ошибка: {e}")
        информация(f"Если ошибка повторяется, напишите автору: {TELEGRAM}")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    print(f"{BLUE}│")
    процесс("Проверяем доступ к серверам...")
    
    servers = cloner.get_servers()
    if not servers:
        ошибка("Не удалось получить список серверов")
        предупреждение("Проверьте токен и подключение к интернету")
        информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    source_exists = any(server.get('id') == source_id for server in servers)
    target_exists = any(server.get('id') == target_id for server in servers)
    
    if not source_exists:
        ошибка("Исходный сервер не найден в вашем списке")
        предупреждение("Убедитесь, что вы есть на этом сервере")
        информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    if not target_exists:
        ошибка("Целевой сервер не найден в вашем списке")
        предупреждение("Убедитесь, что вы есть на этом сервере")
        информация(f"Если проблема не решается, напишите автору: {TELEGRAM}")
        ввод_подсказка("Нажмите Enter для продолжения")
        return
    
    успех("Оба сервера найдены и доступны")
    print(f"{BLUE}│")
    
    clear_screen()
    заголовок("ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ")
    print(f"{BLUE}│")
    предупреждение("ВСЕ СУЩЕСТВУЮЩИЕ КАНАЛЫ И РОЛИ НА ЦЕЛЕВОМ СЕРВЕРЕ БУДУТ УДАЛЕНЫ")
    print(f"{BLUE}│")
    информация("Будет скопировано:")
    информация(f"  {GREEN}•{WHITE} Название сервера")
    информация(f"  {GREEN}•{WHITE} Иконка сервера")
    информация(f"  {GREEN}•{WHITE} Все роли (кроме @everyone)")
    информация(f"  {GREEN}•{WHITE} Все категории и каналы")
    print(f"{BLUE}│")
    информация("НЕ будет скопировано:")
    информация(f"  {RED}•{WHITE} Сообщения в каналах")
    информация(f"  {RED}•{WHITE} Участники сервера")
    информация(f"  {RED}•{WHITE} Вебхуки и интеграции")
    print(f"{BLUE}│")
    ошибка("ОТМЕНИТЬ ЭТО ДЕЙСТВИЕ БУДЕТ НЕВОЗМОЖНО")
    информация(f"При возникновении ошибок пишите автору: {TELEGRAM}")
    print(f"\n{BLUE}└{'─' * 63}┘")
    
    confirm = ввод_подсказка("Вы уверены, что хотите продолжить? (y/N):").strip().lower()
    if confirm not in ['y', 'yes', 'да', 'д']:
        clear_screen()
        заголовок("ОТМЕНА")
        print(f"{BLUE}│")
        ошибка("Операция отменена пользователем")
        print(f"\n{BLUE}└{'─' * 63}┘")
        ввод_подсказка("Нажмите Enter для возврата в меню")
        return
    
    успех("Начинаем клонирование")
    start_time = time.time()
    result = cloner.clone_server(source_id, target_id)
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    if result:
        clear_screen()
        заголовок("КЛОНИРОВАНИЕ ЗАВЕРШЕНО")
        print(f"{BLUE}│")
        успех(f"Время выполнения: {CYAN}{minutes}{WHITE} мин {CYAN}{seconds}{WHITE} сек")
        успех("Все структуры созданы в правильном порядке")
        успех("Перезайдите на сервер, чтобы увидеть все изменения")
    else:
        clear_screen()
        заголовок("КЛОНИРОВАНИЕ НЕ УДАЛОСЬ")
        print(f"{BLUE}│")
        ошибка("Произошла ошибка в процессе клонирования")
        предупреждение("Проверьте логи выше и попробуйте снова")
        информация(f"Если ошибка повторяется, напишите автору: {TELEGRAM}")
    
    print(f"\n{BLUE}└{'─' * 63}┘")
    ввод_подсказка("Нажмите Enter для возврата в меню")

def main_menu():
    печать_баннера()
    подзаголовок("ГЛАВНОЕ МЕНЮ")
    print(f"{BLUE}│")
    информация(f"{GREEN}1.{WHITE} Клонирование сервера")
    информация(f"{GREEN}2.{WHITE} Проверка серверов (получить ID)")
    информация(f"{GREEN}3.{WHITE} Информация о программе")
    информация(f"{GREEN}4.{WHITE} Выход")
    print(f"{BLUE}│")
    
    choice = ввод_подсказка("Выберите вариант (1/2/3/4):").strip()
    
    if choice == "1":
        main_cloner()
        main_menu()
    elif choice == "2":
        check_server_menu()
        main_menu()
    elif choice == "3":
        clear_screen()
        заголовок("ИНФОРМАЦИЯ О ПРОГРАММЕ")
        print(f"{BLUE}│")
        информация(f"Версия: {CYAN}{VERSION}{WHITE}")
        информация(f"Автор: {CYAN}{AUTHOR}{WHITE}")
        информация(f"Discord: {CYAN}{DISCORD}{WHITE}")
        информация(f"Telegram: {CYAN}{TELEGRAM}{WHITE}")
        информация(f"Канал: {CYAN}{SUPPORT_CHANNEL}{WHITE}")
        print(f"{BLUE}│")
        информация("Возможности:")
        информация(f"  {GREEN}•{WHITE} Полное клонирование структуры сервера")
        информация(f"  {GREEN}•{WHITE} Копирование ролей с правами")
        информация(f"  {GREEN}•{WHITE} Копирование категорий и каналов")
        информация(f"  {GREEN}•{WHITE} Копирование иконки сервера")
        информация(f"  {GREEN}•{WHITE} Улучшенная обработка ошибок")
        информация(f"  {GREEN}•{WHITE} Оптимизированные задержки запросов")
        print(f"{BLUE}│")
        информация("При обнаружении ошибок пишите автору:")
        информация(f"Telegram: {CYAN}{TELEGRAM}{WHITE}")
        print(f"\n{BLUE}└{'─' * 63}┘")
        ввод_подсказка("Нажмите Enter для возврата в меню")
        main_menu()
    elif choice == "4":
        clear_screen()
        заголовок("ВЫХОД")
        print(f"{BLUE}│")
        успех("До свидания! Спасибо за использование программы")
        print(f"\n{BLUE}└{'─' * 63}┘")
        time.sleep(1)
        return
    else:
        ошибка("Неверный выбор")
        ввод_подсказка("Нажмите Enter для продолжения")
        main_menu()

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[-]{WHITE} Программа прервана пользователем")
        input(f"{MAGENTA}[?]{WHITE} Нажмите Enter для выхода")
    except Exception as e:
        print(f"\n\n{RED}[-]{WHITE} Критическая ошибка: {type(e).__name__}: {e}")
        print(f"\n{YELLOW}[!]{WHITE} Если ошибка повторяется, напишите автору: {TELEGRAM}")
        input(f"\n{MAGENTA}[?]{WHITE} Нажмите Enter для выхода")
    finally:
        clear_screen()
        print(f"{BLUE}╔{'═' * 63}╗")
        print(f"{BLUE}║ {CYAN}{f'Discord Server Cloner V{VERSION}':^61} {BLUE}║")
        print(f"{BLUE}║ {CYAN}{f'Автор: {AUTHOR} | Поддержка: {TELEGRAM}':^61} {BLUE}║")
        print(f"{BLUE}╚{'═' * 63}╝")

if __name__ == "__main__":
    main()