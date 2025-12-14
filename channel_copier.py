import sys
import os

if sys.platform == "win32":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import Fore, Back, Style, init
import urllib.request
import urllib.error
import json
import ssl
import time
import base64
import aiohttp
import asyncio
import re
from typing import Optional, Dict, List, Any, Tuple
import traceback

init(autoreset=True)

BLUE = Fore.BLUE
CYAN = Fore.CYAN
WHITE = Fore.WHITE
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RED = Fore.RED
MAGENTA = Fore.MAGENTA


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


def debug(text):
    print(f"{MAGENTA}⚙ {WHITE}{text}")


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
        if len(token) < 50:
            return False

        patterns = [
            r'^[A-Za-z0-9\.\-_]{59}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
            r'^[A-Za-z0-9\.\-_]{24}\.[A-Za-z0-9\.\-_]{6}\.[A-Za-z0-9\.\-_]{27}$',
            r'^mfa\.[A-Za-z0-9\.\-_]{84}$',
            r'^[A-Za-z0-9\.\-_]{70,}$'
        ]

        for pattern in patterns:
            if re.match(pattern, token):
                return True

        return False

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
            snowflake_int = int(snowflake)
            return snowflake_int > 10000000000000000
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

        if not cleaned or cleaned.isspace():
            return "канал"

        return cleaned

    @staticmethod
    def clean_role_name(name: str) -> str:
        if not name or not isinstance(name, str):
            return "Новая роль"

        cleaned = DiscordValidator.clean_channel_name(name)
        if cleaned == "канал":
            return "Новая роль"

        return cleaned

    @staticmethod
    def sanitize_permissions(perms: Any) -> str:
        try:
            if isinstance(perms, str):
                perms_int = int(perms)
            elif isinstance(perms, int):
                perms_int = perms
            else:
                perms_int = 0

            if perms_int == 0:
                perms_int = 1024

            max_perms = 0x7FFFFFFFFFFFFFFF
            perms_int = perms_int & max_perms

            return str(perms_int)
        except:
            return "1024"


class RequestManager:

    def __init__(self, headers: Dict[str, str]):
        self.headers = headers.copy()
        self.ssl_context = SafeSSLContext()
        self.max_retries = 3
        self.base_delay = 1.5
        self.timeout = 30

        self.headers.setdefault('User-Agent',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.headers.setdefault('Accept', 'application/json')
        self.headers.setdefault('Accept-Language', 'en-US,en;q=0.9')
        self.headers.setdefault('Connection', 'keep-alive')

    def _handle_rate_limit(self, headers: Dict) -> float:
        retry_after = headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after) + 0.5
            except:
                pass

        reset_after = headers.get('X-RateLimit-Reset-After')
        if reset_after:
            try:
                return float(reset_after) + 0.5
            except:
                pass

        return 2.0

    def _prepare_data(self, data: Any) -> Optional[bytes]:
        if data is None:
            return None

        if isinstance(data, dict) or isinstance(data, list):
            try:
                json_str = json.dumps(data, ensure_ascii=False)
                return json_str.encode('utf-8')
            except Exception as e:
                error(f"Ошибка сериализации JSON: {e}")
                return None

        if isinstance(data, str):
            return data.encode('utf-8')

        if isinstance(data, bytes):
            return data

        try:
            return str(data).encode('utf-8')
        except:
            error(f"Не удалось подготовить данные типа {type(data)}")
            return None

    def request(self, method: str, url: str, data: Any = None) -> Tuple[Optional[Any], Optional[Any]]:
        headers = self.headers.copy()
        if data is not None:
            headers['Content-Type'] = 'application/json'

        for attempt in range(self.max_retries):
            try:
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

                    status = response.status
                    response_data = response.read()

                    if response_data:
                        try:
                            decoded = response_data.decode('utf-8', errors='ignore')
                            if decoded.strip():
                                json_data = json.loads(decoded)
                            else:
                                json_data = None
                        except json.JSONDecodeError:
                            json_data = response_data.decode('utf-8', errors='ignore')
                    else:
                        json_data = None

                    if status == 429:
                        delay = self._handle_rate_limit(response.headers)
                        warning(f"Rate limit. Ждем {delay:.1f} сек...")
                        time.sleep(delay)
                        continue

                    return response, json_data

            except urllib.error.HTTPError as e:
                status = e.code

                if status == 429:
                    delay = self._handle_rate_limit(e.headers)
                    warning(f"Rate limit (HTTPError). Ждем {delay:.1f} сек...")
                    time.sleep(delay)
                    continue

                elif status == 401:
                    error("HTTP 401: Unauthorized - Неверный токен")
                    return None, {"error": "Unauthorized"}

                elif status == 403:
                    error("HTTP 403: Forbidden - Нет прав доступа")
                    return None, {"error": "Forbidden"}

                elif status == 404:
                    error(f"HTTP 404: Not Found - {url}")
                    return None, {"error": "Not Found"}

                else:
                    error(f"HTTP {status}: {e.reason}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.base_delay)
                        continue

                return e, None

            except urllib.error.URLError as e:
                error(f"URLError: {e.reason}")
                time.sleep(3)
                if attempt < self.max_retries - 1:
                    continue

            except ssl.SSLError as e:
                error(f"SSL Error: {e}")
                time.sleep(2)
                if attempt < self.max_retries - 1:
                    continue

            except Exception as e:
                error(f"Unexpected error: {type(e).__name__}: {e}")
                debug(f"Traceback: {traceback.format_exc()}")
                time.sleep(2)
                if attempt < self.max_retries - 1:
                    continue

        error(f"Failed after {self.max_retries} attempts: {method} {url}")
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
            raise ValueError("Invalid Discord token format")

        self.token = token
        self.validator = DiscordValidator()

        self.headers = {
            'Authorization': token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }

        self.request_manager = RequestManager(self.headers)

        self.channel_delay = 1.2
        self.role_delay = 1.5
        self.bulk_delay = 2.0

        self.cache = {}

    def _check_response(self, response, operation: str = "") -> bool:
        if response is None:
            error(f"No response for operation: {operation}")
            return False

        if hasattr(response, 'status'):
            status = response.status
            if 200 <= status < 300:
                return True
            else:
                error(f"Status {status} for operation: {operation}")
                return False

        return False

    def get_server_info(self, server_id: str) -> Optional[Dict]:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return None

        cache_key = f"server_{server_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        url = f'https://discord.com/api/v9/guilds/{server_id}'
        response, data = self.request_manager.get(url)

        if response and hasattr(response, 'status') and response.status == 200:
            if isinstance(data, dict):
                self.cache[cache_key] = data
                return data
            else:
                error(f"Invalid response data for server {server_id}")

        return None

    def get_servers(self) -> List[Dict]:
        url = 'https://discord.com/api/v9/users/@me/guilds'
        response, data = self.request_manager.get(url)

        if response and hasattr(response, 'status'):
            if response.status == 200:
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'message' in data:
                    error(f"Discord API error: {data.get('message')}")
                else:
                    error(f"Invalid response format from Discord API")
            else:
                error(f"HTTP {response.status} при получении серверов")

        return []

    def get_channels(self, server_id: str) -> List[Dict]:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return []

        cache_key = f"channels_{server_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        url = f'https://discord.com/api/v9/guilds/{server_id}/channels'
        response, data = self.request_manager.get(url)

        if self._check_response(response, "get_channels"):
            if isinstance(data, list):
                self.cache[cache_key] = data
                return data

        return []

    def get_roles(self, server_id: str) -> List[Dict]:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return []

        cache_key = f"roles_{server_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        url = f'https://discord.com/api/v9/guilds/{server_id}/roles'
        response, data = self.request_manager.get(url)

        if self._check_response(response, "get_roles"):
            if isinstance(data, list):
                self.cache[cache_key] = data
                return data

        return []

    def get_server_icon(self, server_id: str) -> Optional[str]:
        try:
            server_info = self.get_server_info(server_id)
            if not server_info or not server_info.get('icon'):
                return None

            icon_hash = server_info['icon']

            for size in [256, 128, 64]:
                try:
                    icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon_hash}.png?size={size}"

                    req = urllib.request.Request(icon_url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })

                    with urllib.request.urlopen(req, timeout=30) as response:
                        if response.status == 200:
                            icon_data = response.read()
                            return base64.b64encode(icon_data).decode('utf-8')
                except Exception as e:
                    debug(f"Failed to download icon size {size}: {e}")
                    continue

            return None

        except Exception as e:
            warning(f"Error loading server icon: {e}")
            return None

    def delete_channel(self, channel_id: str) -> bool:
        if not self.validator.validate_snowflake(channel_id):
            error(f"Invalid channel ID: {channel_id}")
            return False

        url = f'https://discord.com/api/v9/channels/{channel_id}'
        response, _ = self.request_manager.delete(url)

        if self._check_response(response, "delete_channel"):
            time.sleep(self.channel_delay * 0.5)
            return True

        return False

    def create_channel(self, server_id: str, channel_data: Dict) -> Tuple[bool, Optional[Dict]]:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return False, None

        sanitized_data = self._sanitize_channel_data(channel_data)
        if not sanitized_data:
            return False, None

        url = f'https://discord.com/api/v9/guilds/{server_id}/channels'
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
            warning(f"Invalid channel type {sanitized['type']}, using 0 (text)")
            sanitized['type'] = 0

        if 'parent_id' in sanitized:
            parent_id = sanitized['parent_id']
            if parent_id and not self.validator.validate_snowflake(str(parent_id)):
                warning(f"Invalid parent_id: {parent_id}, removing")
                del sanitized['parent_id']

        if 'position' in sanitized:
            try:
                sanitized['position'] = int(sanitized['position'])
            except:
                sanitized['position'] = 0

        return sanitized

    def create_role(self, server_id: str, role_data: Dict) -> Tuple[bool, Optional[Dict]]:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return False, None

        sanitized_data = self._sanitize_role_data(role_data)
        if not sanitized_data:
            return False, None

        url = f'https://discord.com/api/v9/guilds/{server_id}/roles'
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
            error(f"Invalid server ID: {server_id}")
            return False

        if not isinstance(position_data, list) or not position_data:
            warning("No position data provided")
            return True

        validated = []
        for item in position_data:
            if not isinstance(item, dict):
                continue

            if 'id' not in item or 'position' not in item:
                continue

            if not self.validator.validate_snowflake(str(item['id'])):
                warning(f"Invalid role ID in position data: {item['id']}")
                continue

            try:
                position = int(item['position'])
                if position < 0:
                    warning(f"Invalid position: {position}")
                    continue
            except:
                warning(f"Invalid position value: {item['position']}")
                continue

            validated.append({
                'id': str(item['id']),
                'position': position
            })

        if not validated:
            warning("No valid position data after validation")
            return True

        url = f'https://discord.com/api/v9/guilds/{server_id}/roles'
        response, _ = self.request_manager.patch(url, validated)

        if self._check_response(response, "update_role_positions"):
            time.sleep(self.bulk_delay)
            return True

        return False

    def update_server_info(self, server_id: str, server_data: Dict) -> bool:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return False

        url = f'https://discord.com/api/v9/guilds/{server_id}'
        response, _ = self.request_manager.patch(url, server_data)

        return self._check_response(response, "update_server_info")

    def delete_role(self, server_id: str, role_id: str) -> bool:
        if not self.validator.validate_snowflake(server_id):
            error(f"Invalid server ID: {server_id}")
            return False

        if not self.validator.validate_snowflake(role_id):
            error(f"Invalid role ID: {role_id}")
            return False

        url = f'https://discord.com/api/v9/guilds/{server_id}/roles/{role_id}'
        response, _ = self.request_manager.delete(url)

        if self._check_response(response, "delete_role"):
            time.sleep(self.role_delay * 0.5)
            return True

        return False

    def clone_server(self, source_id: str, target_id: str) -> bool:
        try:
            header("🚀 ЗАПУСК КЛОНИРОВАНИЯ")

            info("Получаем информацию о серверах...")
            source_info = self.get_server_info(source_id)
            if not source_info:
                error("Не удалось получить информацию об исходном сервере")
                return False

            target_info = self.get_server_info(target_id)
            if not target_info:
                error("Не удалось получить информацию о целевом сервере")
                return False

            source_name = source_info.get('name', 'Неизвестный сервер')
            target_name = target_info.get('name', 'Неизвестный сервер')

            success(f"Исходный сервер: {source_name}")
            success(f"Целевой сервер: {target_name}")

            info("Копируем название сервера...")
            name_data = {'name': source_name}
            if self.update_server_info(target_id, name_data):
                success(f"Название скопировано: {source_name}")
            else:
                warning("Не удалось скопировать название")

            info("Копируем иконку сервера...")
            icon_b64 = self.get_server_icon(source_id)
            if icon_b64:
                try:
                    icon_data = {'icon': f"data:image/png;base64,{icon_b64}"}
                    if self.update_server_info(target_id, icon_data):
                        success("Иконка сервера скопирована")
                    else:
                        warning("Не удалось скопировать иконку")
                except Exception as e:
                    warning(f"Ошибка при обработке иконки: {e}")
            else:
                info("У сервера нет иконки или не удалось ее загрузить")

            info("Анализируем структуры серверов...")
            source_channels = self.get_channels(source_id)
            target_channels = self.get_channels(target_id)
            source_roles = self.get_roles(source_id)
            target_roles = self.get_roles(target_id)

            success(f"Исходный сервер: {len(source_channels)} каналов, {len(source_roles)} ролей")
            warning(f"Целевой сервер: {len(target_channels)} каналов, {len(target_roles)} ролей")

            if not self._clean_target_server(target_id, target_channels, target_roles):
                error("Не удалось очистить целевой сервер")
                return False

            if not self._clone_roles(source_roles, target_id):
                error("Не удалось клонировать роли")
                return False

            if not self._clone_channels(source_channels, target_id):
                error("Не удалось клонировать каналы")
                return False

            header("🎉 КЛОНИРОВАНИЕ ЗАВЕРШЕНО")
            success(f"Сервер '{source_name}' успешно клонирован в '{target_name}'")
            success("Все структуры созданы в правильном порядке")

            return True

        except Exception as e:
            error(f"Критическая ошибка при клонировании: {e}")
            debug(f"Трассировка: {traceback.format_exc()}")
            return False

    def _clean_target_server(self, target_id: str, channels: List[Dict], roles: List[Dict]) -> bool:
        header("🗑️  ОЧИСТКА ЦЕЛЕВОГО СЕРВЕРА")

        if channels:
            info(f"Удаляем {len(channels)} каналов...")
            deleted = 0

            for channel in channels:
                if self.delete_channel(channel['id']):
                    deleted += 1
                    if deleted % 10 == 0:
                        info(f"Удалено {deleted}/{len(channels)} каналов...")
                else:
                    error(f"Не удалось удалить канал: {channel.get('name', 'Unknown')}")

            success(f"Удалено каналов: {deleted}/{len(channels)}")

        time.sleep(self.bulk_delay)

        if roles:
            info(f"Удаляем {len(roles)} ролей...")
            deleted = 0

            sorted_roles = sorted(roles, key=lambda x: x.get('position', 0))

            for role in sorted_roles:
                if role.get('name') == '@everyone' or role.get('managed', False):
                    continue

                if self.delete_role(target_id, role['id']):
                    deleted += 1
                    if deleted % 5 == 0:
                        info(f"Удалено {deleted} ролей...")
                else:
                    error(f"Не удалось удалить роль: {role.get('name', 'Unknown')}")

            success(f"Удалено ролей: {deleted}")

        time.sleep(self.bulk_delay * 2)
        return True

    def _clone_roles(self, source_roles: List[Dict], target_id: str) -> bool:
        header("🎨 КЛОНИРОВАНИЕ РОЛЕЙ")

        roles_to_create = []
        for role in source_roles:
            if role.get('name') == '@everyone' or role.get('managed', False):
                continue
            roles_to_create.append(role)

        if not roles_to_create:
            info("Нет ролей для клонирования")
            return True

        success(f"Будет создано {len(roles_to_create)} ролей")

        sorted_roles = sorted(roles_to_create, key=lambda x: x.get('position', 0), reverse=True)

        role_mapping = {}
        created = 0

        info("Создаем роли...")
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
                    success(f"Создана роль: {role_name} ({i}/{len(sorted_roles)})")
                else:
                    error(f"Не удалось получить ID созданной роли: {role_name}")
            else:
                error(f"Ошибка создания роли: {role_name}")

            if i % 5 == 0 or i == len(sorted_roles):
                info(f"Прогресс: {i}/{len(sorted_roles)} ролей")

        if role_mapping:
            info("Обновляем порядок ролей...")
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

        success(f"Создано ролей: {created}/{len(sorted_roles)}")
        return created > 0

    def _clone_channels(self, source_channels: List[Dict], target_id: str) -> bool:
        header("🏗️  КЛОНИРОВАНИЕ КАНАЛОВ")

        if not source_channels:
            info("Нет каналов для клонирования")
            return True

        categories = [ch for ch in source_channels if ch.get('type') == 4]
        channels = [ch for ch in source_channels if ch.get('type') != 4]

        success(f"Будет создано: {len(categories)} категорий и {len(channels)} каналов")

        category_map = {}
        if categories:
            info("Создаем категории...")

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
                        success(f"Создана категория: {category_name} ({i}/{len(sorted_categories)})")
                    else:
                        error(f"Не удалось получить ID категории: {category_name}")
                else:
                    error(f"Ошибка создания категории: {category_name}")

                if i % 3 == 0 or i == len(sorted_categories):
                    info(f"Прогресс категорий: {i}/{len(sorted_categories)}")

        time.sleep(self.bulk_delay)

        if channels:
            info("Создаем каналы...")

            sorted_channels = sorted(channels, key=lambda x: x.get('position', 0))

            created = 0
            for i, channel in enumerate(sorted_channels, 1):
                channel_name = channel.get('name', f'Канал {i}')
                channel_type = channel.get('type', 0)

                valid_types = [0, 2, 5, 13, 15]
                if channel_type not in valid_types:
                    warning(f"Пропускаем тип {channel_type}: {channel_name}")
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
                    success(f"Создан канал: {channel_name} ({i}/{len(sorted_channels)})")
                else:
                    error(f"Ошибка создания канала: {channel_name}")

                if i % 10 == 0 or i == len(sorted_channels):
                    info(f"Прогресс каналов: {i}/{len(sorted_channels)}")

            success(f"Создано каналов: {created}/{len(sorted_channels)}")

        return True


async def check_servers_async(token: str):
    headers = {
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    async with aiohttp.ClientSession() as session:
        try:
            info("Проверяем токен...")

            async with session.get(
                    'https://discord.com/api/v9/users/@me',
                    headers=headers,
                    timeout=30
            ) as response:

                if response.status == 200:
                    user_data = await response.json()
                    username = user_data.get('username', 'N/A')
                    discriminator = user_data.get('discriminator', '0000')
                    user_id = user_data.get('id', 'N/A')

                    success("✅ ТОКЕН РАБОЧИЙ!")
                    info(f"👤 Пользователь: {username}#{discriminator}")
                    info(f"🆔 ID: {user_id}")
                    info(f"📧 Email: {user_data.get('email', 'Не указан')}")

                    info("Получаем список серверов...")
                    async with session.get(
                            'https://discord.com/api/v9/users/@me/guilds',
                            headers=headers,
                            timeout=30
                    ) as guilds_response:

                        if guilds_response.status == 200:
                            guilds = await guilds_response.json()
                            success(f"📊 Найдено серверов: {len(guilds)}")

                            header("📋 СПИСОК СЕРВЕРОВ")
                            for i, guild in enumerate(guilds, 1):
                                guild_id = guild.get('id', 'N/A')
                                guild_name = guild.get('name', 'Неизвестный сервер')
                                permissions = int(guild.get('permissions', 0))
                                is_admin = (permissions & 0x8) != 0
                                is_owner = guild.get('owner', False)

                                admin_badge = f" {RED}[ADMIN]" if is_admin else ""
                                owner_badge = f" {GREEN}[ВЛАДЕЛЕЦ]" if is_owner else ""
                                icon = " 📷" if guild.get('icon') else ""

                                print(f"{WHITE}{i:3d}. {guild_name}{admin_badge}{owner_badge}{icon}")
                                print(f"    {CYAN}ID: {WHITE}{guild_id}")

                                if i < len(guilds):
                                    print(f"{BLUE}    {'─' * 50}")

                            print(line())
                            success("✅ Все сервера успешно загружены!")
                            info("💡 Скопируйте ID нужного сервера для клонирования")

                        else:
                            error(f"❌ Не удалось получить серверы: {guilds_response.status}")

                else:
                    error(f"❌ Токен невалидный: {response.status}")

        except aiohttp.ClientConnectionError:
            error("❌ Ошибка подключения к Discord")
        except asyncio.TimeoutError:
            error("❌ Таймаут подключения")
        except aiohttp.ClientResponseError as e:
            error(f"❌ Ошибка ответа: {e.status} - {e.message}")
        except Exception as e:
            error(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
            debug(f"Трассировка: {traceback.format_exc()[:200]}")


def check_servers(token: str):
    asyncio.run(check_servers_async(token))


def check_server_menu():
    print_banner()

    info("Выберите способ ввода токена:")
    info("1. 📝 Ввести токен вручную")
    info("2. 📁 Использовать токен из файла")
    info("3. 📖 Инструкция по получению токена")
    info("4. ↩️  Назад в главное меню")

    choice = input_prompt("Выберите вариант (1/2/3/4): ").strip()

    if choice == "4":
        return

    token = ""

    if choice == "1":
        warning("⚠️  Внимание: Токен будет виден при вводе!")
        token = input_field("Введите токен Discord").strip()

    elif choice == "2":
        token_file = "token.txt"
        if os.path.exists(token_file):
            try:
                with open(token_file, "r", encoding="utf-8") as f:
                    token = f.read().strip()
                success(f"✅ Токен загружен из {token_file}")
            except Exception as e:
                error(f"❌ Ошибка чтения файла: {e}")
                input_prompt("Нажмите Enter для продолжения...")
                check_server_menu()
                return
        else:
            error(f"❌ Файл {token_file} не найден!")
            info(f"💡 Создайте файл {token_file} с вашим токеном")
            input_prompt("Нажмите Enter для продолжения...")
            check_server_menu()
            return

    elif choice == "3":
        header("📖 ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ ТОКЕНА")
        print(f"{WHITE}1. Откройте Discord в браузере")
        print(f"{WHITE}2. Нажмите {CYAN}F12 {WHITE}(DevTools)")
        print(f"{WHITE}3. Перейдите на вкладку {CYAN}'Network'")
        print(f"{WHITE}4. Обновите страницу ({CYAN}F5{WHITE})")
        print(f"{WHITE}5. Найдите запрос к {CYAN}discord.com")
        print(f"{WHITE}6. В разделе {CYAN}'Headers' {WHITE}найдите {CYAN}'Authorization'")
        print(f"{WHITE}7. Скопируйте токен (начинается с букв)")
        print(f"\n{RED}⚠️  ВАЖНО: Никому не передавайте ваш токен!")
        print(f"{RED}⚠️  Токен дает полный доступ к вашему аккаунту!")
        print(f"{BLUE}═" * 65)
        input_prompt("Нажмите Enter для возврата...")
        check_server_menu()
        return

    else:
        error("❌ Неверный выбор!")
        input_prompt("Нажмите Enter для продолжения...")
        check_server_menu()
        return

    if not token:
        error("❌ Токен не может быть пустым!")
        input_prompt("Нажмите Enter для продолжения...")
        check_server_menu()
        return

    if not DiscordValidator.validate_token(token):
        error("❌ Неверный формат токена!")
        info("💡 Токен должен быть длинной строкой (50+ символов)")
        input_prompt("Нажмите Enter для продолжения...")
        check_server_menu()
        return

    check_servers(token)
    input_prompt("Нажмите Enter для возврата в меню...")


def main_cloner():
    if not confirm_agreement():
        error("❌ Вы не подтвердили пользовательское соглашение!")
        input_prompt("Нажмите Enter для выхода...")
        return

    print_banner()

    info("Введите данные для клонирования:")

    token = input_field("Токен Discord").strip()
    if not token:
        error("❌ Токен не может быть пустым!")
        input_prompt("Нажмите Enter для продолжения...")
        return

    if not DiscordValidator.validate_token(token):
        error("❌ Неверный формат токена!")
        input_prompt("Нажмите Enter для продолжения...")
        return

    source_id = input_field("ID исходного сервера").strip()
    if not source_id or not DiscordValidator.validate_snowflake(source_id):
        error("❌ Неверный ID исходного сервера!")
        input_prompt("Нажмите Enter для продолжения...")
        return

    target_id = input_field("ID целевого сервера").strip()
    if not target_id or not DiscordValidator.validate_snowflake(target_id):
        error("❌ Неверный ID целевого сервера!")
        input_prompt("Нажмите Enter для продолжения...")
        return

    if source_id == target_id:
        error("❌ Исходный и целевой сервер не могут быть одинаковыми!")
        input_prompt("Нажмите Enter для продолжения...")
        return

    try:
        cloner = AdvancedCloner(token)
    except ValueError as e:
        error(f"❌ Ошибка инициализации: {e}")
        input_prompt("Нажмите Enter для продолжения...")
        return
    except Exception as e:
        error(f"❌ Неожиданная ошибка: {e}")
        input_prompt("Нажмите Enter для продолжения...")
        return

    info("🔍 Проверяем доступ к серверам...")
    servers = cloner.get_servers()

    if not servers:
        error("❌ Не удалось получить список серверов!")
        warning("💡 Проверьте токен и подключение к интернету")
        input_prompt("Нажмите Enter для продолжения...")
        return

    source_exists = any(server.get('id') == source_id for server in servers)
    target_exists = any(server.get('id') == target_id for server in servers)

    if not source_exists:
        error("❌ Исходный сервер не найден в вашем списке!")
        warning("💡 Убедитесь, что вы есть на этом сервере")
        input_prompt("Нажмите Enter для продолжения...")
        return

    if not target_exists:
        error("❌ Целевой сервер не найден в вашем списке!")
        warning("💡 Убедитесь, что вы есть на этом сервере")
        input_prompt("Нажмите Enter для продолжения...")
        return

    success("✅ Оба сервера найдены и доступны!")

    header("⚠️  ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ")
    print(f"{RED}✖ {WHITE}ВСЕ СУЩЕСТВУЮЩИЕ КАНАЛЫ И РОЛИ НА ЦЕЛЕВОМ СЕРВЕРЕ БУДУТ УДАЛЕНЫ!")
    print(f"\n{YELLOW}! {WHITE}Будет скопировано:")
    print(f"   {CYAN}• {WHITE}Название сервера")
    print(f"   {CYAN}• {WHITE}Иконка сервера")
    print(f"   {CYAN}• {WHITE}Все роли (кроме @everyone)")
    print(f"   {CYAN}• {WHITE}Все категории и каналы")
    print(f"\n{YELLOW}! {WHITE}НЕ будет скопировано:")
    print(f"   {CYAN}• {WHITE}Сообщения в каналах")
    print(f"   {CYAN}• {WHITE}Участники сервера")
    print(f"   {CYAN}• {WHITE}Вебхуки и интеграции")
    print(f"\n{RED}⚠️  ОТМЕНИТЬ ЭТО ДЕЙСТВИЕ БУДЕТ НЕВОЗМОЖНО!")
    print(f"{BLUE}═" * 65)

    confirm = input_prompt("Вы уверены, что хотите продолжить? (y/N): ").strip().lower()

    if confirm not in ['y', 'yes', 'да']:
        error("❌ Операция отменена пользователем")
        input_prompt("Нажмите Enter для возврата в мену...")
        return

    success("🚀 Начинаем клонирование...")
    start_time = time.time()

    result = cloner.clone_server(source_id, target_id)

    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    if result:
        header("🎉 КЛОНИРОВАНИЕ УСПЕШНО ЗАВЕРШЕНО!")
        success(f"⏱️  Время выполнения: {minutes} мин {seconds} сек")
        success("✅ Все структуры созданы в правильном порядке")
        success("🔄 Перезайдите на сервер, чтобы увидеть все изменения")
    else:
        header("❌ КЛОНИРОВАНИЕ НЕ УДАЛОСЬ")
        error("⚠️  Произошла ошибка в процессе клонирования")
        warning("💡 Проверьте логи выше и попробуйте снова")

    print(f"{BLUE}═" * 65)
    input_prompt("Нажмите Enter для возврата в меню...")


def main_menu():
    print_banner()

    info("Выберите режим работы:")
    info("1. 🚀 Клонирование сервера")
    info("2. 🔍 Проверка серверов (получить ID)")
    info("3. ❌ Выход")

    choice = input_prompt("Выберите вариант (1/2/3): ").strip()

    if choice == "1":
        main_cloner()
        main_menu()
    elif choice == "2":
        check_server_menu()
        main_menu()
    elif choice == "3":
        success("👋 До свидания! Спасибо за использование программы!")
        time.sleep(1)
        return
    else:
        error("❌ Неверный выбор!")
        input_prompt("Нажмите Enter для продолжения...")
        main_menu()


def main():
    try:
        main_menu()

    except KeyboardInterrupt:
        print(f"\n\n{RED}✖ Программа прервана пользователем")
        input_prompt("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"\n\n{RED}✖ Критическая ошибка: {type(e).__name__}: {e}")
        print(f"{YELLOW}Трассировка:{WHITE}")
        traceback.print_exc()
        input_prompt("\nНажмите Enter для выхода...")
    finally:
        print(f"\n{BLUE}═" * 65)
        print(f"{CYAN}Discord Server Cloner V3 — BLUE EDITION")
        print(f"{CYAN}Автор: zlafik | Discord: zlafik | Telegram: @zlafik")
        print(f"{BLUE}═" * 65)


if __name__ == "__main__":
    main()