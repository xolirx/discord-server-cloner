import urllib.request
import urllib.error
import json
import ssl
import time
import base64
import os
from colorama import init, Fore, Back, Style

init(autoreset=True)

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
                print(f"{Fore.YELLOW}⚠️  Rate limit, ждем {retry_after} секунд...")
                time.sleep(float(retry_after))
                return self.make_request(method, url, data)
            print(f"{Fore.RED}❌ HTTP Error {e.code}: {e.reason}")
            if e.code == 401:
                print(f"{Fore.RED}🔑 Неверный токен!")
            elif e.code == 403:
                print(f"{Fore.RED}🚫 Нет прав доступа!")
            return e, None
        except Exception as e:
            print(f"{Fore.RED}❌ Request Error: {e}")
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
            print(f"{Fore.YELLOW}⚠️  Ошибка загрузки аватарки: {e}")
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
                    print(f"{Fore.YELLOW}⚠️  Неожиданный статус код: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"{Fore.YELLOW}⚠️  Rate limit, ждем...")
                time.sleep(2)
                return self.delete_role(server_id, role_id)
            print(f"{Fore.RED}❌ HTTP Error {e.code} при удалении роли: {e.reason}")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Request Error при удалении роли: {e}")
            return False
    
    def clone_server(self, source_id, target_id):
        print(f"\n{Fore.CYAN}🚀 Запускаем клонирование...")
        print(f"{Fore.CYAN}{'═' * 60}")
        
        print(f"{Fore.MAGENTA}📡 Получаем информацию о серверах...")
        source_info = self.get_server_info(source_id)
        if not source_info:
            print(f"{Fore.RED}❌ Не удалось получить информацию об исходном сервере!")
            return
        
        server_name = source_info.get('name', 'Unknown Server')
        
        print(f"\n{Fore.BLUE}📝 Копируем название сервера...")
        name_data = {'name': server_name}
        if self.update_server_info(target_id, name_data):
            print(f"{Fore.GREEN}✅ Название скопировано: {Fore.WHITE}{server_name}")
        else:
            print(f"{Fore.RED}❌ Ошибка копирования названия")
        
        print(f"\n{Fore.BLUE}🖼️  Копируем аватарку сервера...")
        server_icon_b64 = self.get_server_icon(source_id)
        if server_icon_b64:
            try:
                icon_data = {'icon': f"data:image/png;base64,{server_icon_b64}"}
                if self.update_server_info(target_id, icon_data):
                    print(f"{Fore.GREEN}✅ Аватарка скопирована!")
                else:
                    print(f"{Fore.RED}❌ Ошибка копирования аватарки")
            except Exception as e:
                print(f"{Fore.RED}❌ Ошибка при обработке аватарки: {e}")
        else:
            print(f"{Fore.YELLOW}⚠️  У исходного сервера нет аватарки")
        
        print(f"{Fore.MAGENTA}📊 Анализируем структуру серверов...")
        source_channels = self.get_channels(source_id)
        target_channels = self.get_channels(target_id)
        source_roles = self.get_roles(source_id)
        target_roles = self.get_roles(target_id)
        
        print(f"{Fore.GREEN}📁 Исходный сервер: {len(source_channels)} каналов, {len(source_roles)} ролей")
        print(f"{Fore.YELLOW}📁 Целевой сервер: {len(target_channels)} каналов, {len(target_roles)} ролей")
        
        print(f"\n{Fore.RED}🗑️  Очищаем целевой сервер...")
        print(f"{Fore.RED}├── Удаляем каналы...")
        channels_deleted = 0
        for channel in target_channels:
            if self.delete_channel(channel['id']):
                print(f"{Fore.GREEN}│   ✅ Удален: {channel['name']}")
                channels_deleted += 1
            else:
                print(f"{Fore.RED}│   ❌ Ошибка: {channel['name']}")
            time.sleep(self.rate_limit_delay)
        
        print(f"{Fore.RED}└── Удаляем роли...")
        roles_deleted = 0
        for role in target_roles:
            if not role['managed'] and role['name'] != '@everyone':
                if self.delete_role(target_id, role['id']):
                    print(f"{Fore.GREEN}    ✅ Удалена: {role['name']}")
                    roles_deleted += 1
                else:
                    print(f"{Fore.RED}    ❌ Ошибка: {role['name']}")
                time.sleep(self.rate_limit_delay)
        
        print(f"{Fore.GREEN}✅ Удалено: {channels_deleted} каналов, {roles_deleted} ролей")
        
        print(f"\n{Fore.MAGENTA}🎨 Создаем роли...")
        
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
            
            success, response_data = self.create_role(target_id, role_data)
            if success:
                role_mapping[role['name']] = response_data['id']
                print(f"{Fore.GREEN}✅ Создана роль: {role['name']}")
                role_count += 1
            else:
                print(f"{Fore.RED}❌ Ошибка создания: {role['name']}")
            time.sleep(self.rate_limit_delay)
        
        print(f"\n{Fore.BLUE}📊 Устанавливаем порядок ролей...")
        
        if role_mapping:
            position_updates = []
            for source_role in sorted_roles:
                if source_role['name'] in role_mapping:
                    position_updates.append({
                        'id': role_mapping[source_role['name']],
                        'position': source_role['position']
                    })
            
            if position_updates and self.update_role_positions(target_id, position_updates):
                print(f"{Fore.GREEN}✅ Порядок ролей обновлен!")
            else:
                print(f"{Fore.YELLOW}⚠️  Не удалось обновить порядок ролей")
        else:
            print(f"{Fore.YELLOW}⚠️  Нет ролей для обновления позиций")
        
        print(f"\n{Fore.CYAN}🏗️  Создаем структуру каналов...")
        
        categories = [ch for ch in source_channels if ch['type'] == 4]
        category_map = {}
        
        print(f"{Fore.BLUE}📂 Создаем категории...")
        for category in categories:
            category_data = {
                'name': category['name'],
                'type': 4,
                'position': category['position']
            }
            
            success, data = self.create_channel(target_id, category_data)
            if success:
                category_map[category['id']] = data['id']
                print(f"{Fore.GREEN}✅ Создана категория: {category['name']}")
            else:
                print(f"{Fore.RED}❌ Ошибка создания категории: {category['name']}")
            time.sleep(self.rate_limit_delay)
        
        created_count = 0
        channels = [ch for ch in source_channels if ch['type'] != 4]
        
        print(f"{Fore.BLUE}📝 Создаем каналы...")
        for channel in channels:
            channel_data = {
                'name': channel['name'],
                'type': channel['type'],
                'position': channel['position']
            }
            
            if channel.get('parent_id') and channel['parent_id'] in category_map:
                channel_data['parent_id'] = category_map[channel['parent_id']]
            
            success, _ = self.create_channel(target_id, channel_data)
            if success:
                print(f"{Fore.GREEN}✅ Создан канал: {channel['name']}")
                created_count += 1
            else:
                print(f"{Fore.RED}❌ Ошибка создания: {channel['name']}")
            time.sleep(self.rate_limit_delay)
        
        print(f"\n{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.MAGENTA}🎉 КЛОНИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f"{Fore.CYAN}{'═' * 60}")
        print(f"{Fore.GREEN}✅ Название сервера: {Fore.WHITE}{server_name}")
        print(f"{Fore.GREEN}✅ Создано категорий: {Fore.WHITE}{len(categories)}")
        print(f"{Fore.GREEN}✅ Создано каналов: {Fore.WHITE}{created_count}")
        print(f"{Fore.GREEN}✅ Создано ролей: {Fore.WHITE}{role_count}")
        if server_icon_b64:
            print(f"{Fore.GREEN}✅ Аватарка сервера: {Fore.WHITE}Скопирована")
        print(f"{Fore.CYAN}{'═' * 60}")

def print_banner():
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.MAGENTA}{Back.BLACK}           🚀 Discord Server Cloner V3")
    print(f"{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.YELLOW}👤 Автор: {Fore.WHITE}zlafik")
    print(f"{Fore.YELLOW}📞 Discord: {Fore.WHITE}zlafik")
    print(f"{Fore.YELLOW}📱 Telegram: {Fore.WHITE}@zlafik")
    print(f"{Fore.YELLOW}📢 Telegram Channel: {Fore.WHITE}@biozlafik")
    print(f"{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.GREEN}🎯 ОСОБЕННОСТИ:")
    print(f"{Fore.GREEN}✅ Копирование названия и аватарки")
    print(f"{Fore.GREEN}✅ Создание ролей и каналов")
    print(f"{Fore.GREEN}✅ Сохранение структуры сервера")
    print(f"{Fore.GREEN}✅ Правильный порядок ролей")
    print(f"{Fore.GREEN}✅ Улучшенная обработка ошибок")
    print(f"{Fore.CYAN}{'═' * 60}")

def main():
    print_banner()
    
    print(f"\n{Fore.WHITE}Введите данные для клонирования:")
    
    print(f"\n{Fore.YELLOW}[ТОКЕН] {Fore.WHITE}Токен вашего Discord аккаунта")
    print(f"{Fore.CYAN}>> {Fore.WHITE}Нужен для доступа к API Discord")
    token = input(f"{Fore.GREEN}[ВВОД] Введите токен: {Fore.WHITE}").strip()
    
    if not token:
        print(f"{Fore.RED}❌ Токен не может быть пустым!")
        return
    
    print(f"\n{Fore.YELLOW}[ИСХОДНЫЙ СЕРВЕР] {Fore.WHITE}ID сервера, который копируем")
    print(f"{Fore.CYAN}>> {Fore.WHITE}Берем из Check server.py или через Разработчика (F12)")
    source_id = input(f"{Fore.GREEN}[ВВОД] ID исходного сервера: {Fore.WHITE}").strip()
    
    print(f"\n{Fore.YELLOW}[ЦЕЛЕВОЙ СЕРВЕР] {Fore.WHITE}ID пустого сервера, куда копируем")
    print(f"{Fore.CYAN}>> {Fore.WHITE}Создайте новый сервер или используйте существующий")
    target_id = input(f"{Fore.GREEN}[ВВОД] ID целевого сервера: {Fore.WHITE}").strip()
    
    cloner = AdvancedCloner(token)
    
    print(f"\n{Fore.CYAN}🔍 Проверяем доступ к серверам...")
    servers = cloner.get_servers()
    source_exists = any(s['id'] == source_id for s in servers)
    target_exists = any(s['id'] == target_id for s in servers)
    
    if not source_exists:
        print(f"{Fore.RED}❌ Исходный сервер не найден!")
        print(f"{Fore.YELLOW}💡 Убедитесь, что у вас есть доступ к этому серверу")
        return
    if not target_exists:
        print(f"{Fore.RED}❌ Целевой сервер не найден!")
        print(f"{Fore.YELLOW}💡 Убедитесь, что у вас есть доступ к этому серверу")
        return
    
    print(f"{Fore.GREEN}✅ Серверы найдены и доступны!")
    
    print(f"\n{Fore.RED}{'⚠' * 60}")
    print(f"{Fore.RED}🚨 ВНИМАНИЕ: ВСЕ КАНАЛЫ И РОЛИ НА ЦЕЛЕВОМ СЕРВЕРЕ БУДУТ УДАЛЕНЫ!")
    print(f"{Fore.YELLOW}💡 Будет скопировано: название, аватарка, роли, категории, каналы")
    print(f"{Fore.RED}{'⚠' * 60}")
    confirm = input(f"{Fore.GREEN}[ПОДТВЕРЖДЕНИЕ] Начать клонирование? (y/n): {Fore.WHITE}").lower()
    
    if confirm == 'y':
        print(f"\n{Fore.CYAN}🚀 Запускаем процесс клонирования...")
        cloner.clone_server(source_id, target_id)
    else:
        print(f"{Fore.RED}❌ Операция отменена пользователем")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Произошла ошибка: {e}")
    
    input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")