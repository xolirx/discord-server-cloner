# channel_copier.py
import urllib.request
import urllib.error
import json
import ssl
import time
import base64
import os
from colorama import init, Fore, Back, Style

# Инициализация colorama для цветного вывода
init(autoreset=True)

# Отключаем SSL проверку
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class SimpleCloner:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
    
    def make_request(self, method, url, data=None):
        """Простой HTTP запрос"""
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
                print(f"{Fore.YELLOW}⚠️  Rate limit, ждем 2 секунды...")
                time.sleep(2)
                return self.make_request(method, url, data)
            print(f"{Fore.RED}❌ HTTP Error {e.code}: {e.reason}")
            return e, None
        except Exception as e:
            print(f"{Fore.RED}❌ Request Error: {e}")
            return None, e
    
    def get_server_info(self, server_id):
        """Получаем информацию о сервере"""
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}')
        if response and response.status == 200:
            return data
        return None
    
    def get_servers(self):
        """Получаем список серверов"""
        response, data = self.make_request('GET', 'https://discord.com/api/v9/users/@me/guilds')
        if response and response.status == 200:
            return data
        return []
    
    def get_channels(self, server_id):
        """Получаем каналы сервера"""
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}/channels')
        if response and response.status == 200:
            return data
        return []
    
    def get_roles(self, server_id):
        """Получаем роли сервера"""
        response, data = self.make_request('GET', f'https://discord.com/api/v9/guilds/{server_id}/roles')
        if response and response.status == 200:
            return data
        return []
    
    def get_server_icon(self, server_id):
        """Получаем аватарку сервера"""
        try:
            server_info = self.get_server_info(server_id)
            if server_info and server_info.get('icon'):
                icon_hash = server_info['icon']
                icon_url = f"https://cdn.discordapp.com/icons/{server_id}/{icon_hash}.png?size=4096"
                with urllib.request.urlopen(icon_url, context=ssl_context) as icon_response:
                    icon_data = icon_response.read()
                    return f"data:image/png;base64,{base64.b64encode(icon_data).decode()}"
            return None
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Ошибка загрузки аватарки: {e}")
            return None
    
    def delete_channel(self, channel_id):
        """Удаляем канал"""
        response, _ = self.make_request('DELETE', f'https://discord.com/api/v9/channels/{channel_id}')
        return response and response.status == 200
    
    def create_channel(self, server_id, channel_data):
        """Создаем канал"""
        response, data = self.make_request('POST', f'https://discord.com/api/v9/guilds/{server_id}/channels', channel_data)
        return response and response.status == 201
    
    def create_role(self, server_id, role_data):
        """Создаем роль"""
        response, data = self.make_request('POST', f'https://discord.com/api/v9/guilds/{server_id}/roles', role_data)
        return response and response.status == 200
    
    def update_role_positions(self, server_id, position_data):
        """Обновляем позиции ролей массово - КЛЮЧЕВОЙ МЕТОД ДЛЯ ПОРЯДКА РОЛЕЙ"""
        response, result = self.make_request('PATCH', f'https://discord.com/api/v9/guilds/{server_id}/roles', position_data)
        return response and response.status == 200
    
    def update_server_info(self, server_id, server_data):
        """Обновляем информацию о сервере"""
        response, result = self.make_request('PATCH', f'https://discord.com/api/v9/guilds/{server_id}', server_data)
        return response and response.status == 200
    
    def delete_role(self, server_id, role_id):
        """Удаляем роль"""
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
        """Клонируем сервер V2 - с правильным порядком ролей"""
        print(f"\n{Fore.CYAN}🚀 Начинаем клонирование V2 (правильный порядок ролей)...")
        
        # Получаем информацию об исходном сервере
        source_info = self.get_server_info(source_id)
        if not source_info:
            print(f"{Fore.RED}❌ Не удалось получить информацию об исходном сервере!")
            return
        
        server_name = source_info.get('name', 'Unknown Server')
        
        # Копируем название сервера
        print(f"\n{Fore.MAGENTA}📝 Копируем название сервера...")
        name_data = {'name': server_name}
        if self.update_server_info(target_id, name_data):
            print(f"{Fore.GREEN}✅ Название скопировано: {server_name}")
        else:
            print(f"{Fore.RED}❌ Ошибка копирования названия")
        
        # Копируем аватарку
        print(f"\n{Fore.MAGENTA}🖼️  Копируем аватарку сервера...")
        server_icon = self.get_server_icon(source_id)
        if server_icon:
            icon_data = {'icon': server_icon}
            if self.update_server_info(target_id, icon_data):
                print(f"{Fore.GREEN}✅ Аватарка скопирована!")
            else:
                print(f"{Fore.RED}❌ Ошибка копирования аватарки")
        else:
            print(f"{Fore.YELLOW}⚠️  У исходного сервера нет аватарки")
        
        # Получаем каналы и роли
        source_channels = self.get_channels(source_id)
        target_channels = self.get_channels(target_id)
        source_roles = self.get_roles(source_id)
        target_roles = self.get_roles(target_id)
        
        print(f"{Fore.GREEN}📁 Исходный сервер: {len(source_channels)} каналов, {len(source_roles)} ролей")
        print(f"{Fore.YELLOW}📁 Целевой сервер: {len(target_channels)} каналов, {len(target_roles)} ролей")
        
        # Удаляем старые каналы
        print(f"\n{Fore.RED}🗑️  Удаляем старые каналы...")
        for channel in target_channels:
            if self.delete_channel(channel['id']):
                print(f"{Fore.GREEN}✅ Удален канал: {channel['name']}")
            else:
                print(f"{Fore.RED}❌ Ошибка удаления: {channel['name']}")
            time.sleep(0.5)
        
        # Удаляем старые роли (кроме @everyone)
        print(f"\n{Fore.RED}🗑️  Удаляем старые роли...")
        roles_deleted = 0
        for role in target_roles:
            if not role['managed'] and role['name'] != '@everyone':
                if self.delete_role(target_id, role['id']):
                    print(f"{Fore.GREEN}✅ Удалена роль: {role['name']}")
                    roles_deleted += 1
                else:
                    print(f"{Fore.RED}❌ Ошибка удаления: {role['name']}")
                time.sleep(0.5)
        
        print(f"{Fore.GREEN}✅ Удалено ролей: {roles_deleted}")
        
        # СОЗДАЕМ РОЛИ С ПРАВИЛЬНЫМ ПОРЯДКОМ V2
        print(f"\n{Fore.BLUE}🎨 Создаем новые роли V2 (с правильным порядком)...")
        
        # Фильтруем роли (кроме @everyone и управляемых)
        roles_to_create = [role for role in source_roles if not role['managed'] and role['name'] != '@everyone']
        
        # Сортируем роли по позиции (от высшей к низшей)
        sorted_roles = sorted(roles_to_create, key=lambda x: x['position'], reverse=True)
        
        role_count = 0
        created_roles = []  # Сохраняем созданные роли для обновления позиций
        
        for role in sorted_roles:
            role_data = {
                'name': role['name'],
                'color': role['color'],
                'hoist': role['hoist'],
                'mentionable': role['mentionable'],
                'permissions': str(role['permissions'])
            }
            
            if self.create_role(target_id, role_data):
                # Получаем ID созданной роли (нужно получить список ролей снова)
                print(f"{Fore.GREEN}✅ Создана роль: {role['name']} (позиция: {role['position']})")
                role_count += 1
            else:
                print(f"{Fore.RED}❌ Ошибка создания: {role['name']}")
            time.sleep(0.5)
        
        # ОБНОВЛЯЕМ ПОЗИЦИИ РОЛЕЙ МАССОВО - КЛЮЧЕВОЙ МОМЕНТ!
        print(f"\n{Fore.BLUE}📊 Обновляем порядок ролей массово...")
        
        # Получаем свежий список созданных ролей
        new_roles = self.get_roles(target_id)
        if new_roles:
            # Создаем карту соответствия имен ролей и их ID
            role_name_to_id = {role['name']: role['id'] for role in new_roles if role['name'] != '@everyone'}
            
            # Подготавливаем данные для массового обновления позиций
            position_updates = []
            for source_role in sorted_roles:
                if source_role['name'] in role_name_to_id:
                    position_updates.append({
                        'id': role_name_to_id[source_role['name']],
                        'position': source_role['position']
                    })
            
            # Отправляем массовый запрос на обновление позиций
            if position_updates and self.update_role_positions(target_id, position_updates):
                print(f"{Fore.GREEN}✅ Порядок ролей успешно обновлен!")
                print(f"{Fore.GREEN}✅ Роли расположены в точности как на исходном сервере!")
            else:
                print(f"{Fore.YELLOW}⚠️  Не удалось обновить порядок ролей")
        else:
            print(f"{Fore.RED}❌ Не удалось получить список созданных ролей")
        
        # Создаем категории и каналы
        print(f"\n{Fore.BLUE}📝 Создаем структуру сервера...")
        
        # Сначала создаем категории
        categories = [ch for ch in source_channels if ch['type'] == 4]
        category_map = {}
        
        print(f"{Fore.CYAN}📂 Создаем категории...")
        for category in categories:
            category_data = {
                'name': category['name'],
                'type': 4,
                'position': category['position']
            }
            
            response, data = self.make_request('POST', f'https://discord.com/api/v9/guilds/{target_id}/channels', category_data)
            if response and response.status == 201:
                category_map[category['id']] = data['id']
                print(f"{Fore.GREEN}✅ Создана категория: {category['name']}")
            else:
                print(f"{Fore.RED}❌ Ошибка создания категории: {category['name']}")
            time.sleep(0.5)
        
        # Затем создаем каналы внутри категорий
        created_count = 0
        channels = [ch for ch in source_channels if ch['type'] != 4]
        
        print(f"{Fore.CYAN}📝 Создаем каналы...")
        for channel in channels:
            channel_data = {
                'name': channel['name'],
                'type': channel['type'],
                'position': channel['position']
            }
            
            if channel.get('parent_id') and channel['parent_id'] in category_map:
                channel_data['parent_id'] = category_map[channel['parent_id']]
            
            if self.create_channel(target_id, channel_data):
                print(f"{Fore.GREEN}✅ Создан канал: {channel['name']}")
                created_count += 1
            else:
                print(f"{Fore.RED}❌ Ошибка создания: {channel['name']}")
            time.sleep(0.5)
        
        print(f"\n{Fore.CYAN}🎉 Готово! Клонирование V2 завершено!")
        print(f"{Fore.GREEN}✅ Название сервера: {server_name}")
        print(f"{Fore.GREEN}✅ Создано {len(categories)} категорий, {created_count} каналов и {role_count} ролей!")
        print(f"{Fore.GREEN}✅ Порядок ролей: ТОЧНО как на исходном сервере!")
        if server_icon:
            print(f"{Fore.GREEN}✅ Аватарка сервера скопирована!")

def print_banner():
    """Красивый баннер"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.MAGENTA}{Back.BLACK}           Discord Server Cloner V2")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}👤 Автор: {Fore.WHITE}zlafik")
    print(f"{Fore.YELLOW}📞 Контакт: {Fore.WHITE}discord - stylesx2w2")
    print(f"{Fore.YELLOW}📺 YouTube: {Fore.WHITE}https://www.youtube.com/@stylesxwx")
    print(f"{Fore.YELLOW}📱 Telegram: {Fore.WHITE}https://t.me/peredoznikbio")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}🎯 ОСОБЕННОСТИ V2:")
    print(f"{Fore.GREEN}✅ Правильный порядок ролей")
    print(f"{Fore.GREEN}✅ Точная иерархия как на исходном сервере")
    print(f"{Fore.CYAN}{'='*60}")

def main():
    print_banner()
    
    # Ввод данных с описанием
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
    
    # Проверяем токен
    cloner = SimpleCloner(token)
    
    # Проверяем доступ к серверам
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
        print(f"{Fore.YELLOW}💡 Убедитесь, что у вас есть доступ к этому сервере")
        return
    
    print(f"{Fore.GREEN}✅ Серверы найдены и доступны!")
    
    # Подтверждение
    print(f"\n{Fore.RED}⚠️  ВНИМАНИЕ: Все каналы и роли на целевом сервере будут удалены!")
    print(f"{Fore.YELLOW}💡 Будет скопировано: название, аватарка, роли (с ПРАВИЛЬНЫМ порядком), категории, каналы")
    confirm = input(f"{Fore.GREEN}[ПОДТВЕРЖДЕНИЕ] Начать клонирование? (y/n): {Fore.WHITE}").lower()
    if confirm == 'y':
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
