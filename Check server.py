# Check server.py
import aiohttp
import asyncio
from colorama import init, Fore, Back, Style

# Инициализация colorama для цветного вывода
init(autoreset=True)

def print_banner():
    """Красивый баннер"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.MAGENTA}{Back.BLACK}        Discord Server Checker")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}👤 Автор: {Fore.WHITE}zqmpi")
    print(f"{Fore.YELLOW}📞 Контакт: {Fore.WHITE}discord - stylesx2w2")
    print(f"{Fore.YELLOW}📺 YouTube: {Fore.WHITE}https://www.youtube.com/@stylesxwx")
    print(f"{Fore.CYAN}{'='*60}")

async def check_servers(token):
    headers = {'Authorization': token}
    
    async with aiohttp.ClientSession() as session:
        # Проверяем токен
        print(f"\n{Fore.CYAN}🔍 Проверяем токен...")
        async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as r:
            if r.status == 200:
                user = await r.json()
                print(f"{Fore.GREEN}✅ ТОКЕН РАБОЧИЙ!")
                print(f"{Fore.CYAN}👤 Пользователь: {Fore.WHITE}{user['username']}#{user['discriminator']}")
                print(f"{Fore.CYAN}🆔 ID пользователя: {Fore.WHITE}{user['id']}")
                
                # Получаем список серверов
                print(f"\n{Fore.CYAN}📂 Получаем список серверов...")
                async with session.get('https://discord.com/api/v9/users/@me/guilds', headers=headers) as guilds_r:
                    if guilds_r.status == 200:
                        guilds = await guilds_r.json()
                        print(f"{Fore.GREEN}✅ Найдено серверов: {len(guilds)}")
                        
                        print(f"\n{Fore.CYAN}📋 Список серверов:")
                        print(f"{Fore.CYAN}{'-'*40}")
                        
                        for guild in guilds:
                            guild_id = guild['id']
                            guild_name = guild['name']
                            print(f"{Fore.WHITE}   🏠 {guild_name} (ID: {guild_id})")
                        
                        print(f"{Fore.CYAN}{'-'*40}")
                        print(f"\n{Fore.GREEN}🎉 Все сервера загружены успешно!")
                            
                    else:
                        print(f"{Fore.RED}❌ Не удалось получить список серверов: {guilds_r.status}")
            else:
                print(f"{Fore.RED}❌ Токен невалидный: {r.status}")

def main():
    print_banner()
    
    # Выбор способа ввода токена
    print(f"\n{Fore.YELLOW}🔐 Выберите способ ввода токена:")
    print(f"{Fore.CYAN}1. {Fore.WHITE}Ввести токен вручную")
    print(f"{Fore.CYAN}2. {Fore.WHITE}Использовать токен из файла")
    
    choice = input(f"\n{Fore.YELLOW}[?] Выберите вариант (1/2): {Fore.WHITE}").strip()
    
    token = ""
    
    if choice == "1":
        # Ввод токена вручную
        print(f"\n{Fore.YELLOW}📝 Введите ваш Discord токен:")
        print(f"{Fore.RED}⚠️  Внимание: Токен будет виден при вводе!")
        token = input(f"{Fore.YELLOW}[?] Токен: {Fore.WHITE}").strip()
        
    elif choice == "2":
        # Чтение токена из файла
        try:
            with open("token.txt", "r", encoding="utf-8") as f:
                token = f.read().strip()
            print(f"{Fore.GREEN}✅ Токен успешно загружен из файла token.txt")
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Файл token.txt не найден!")
            print(f"{Fore.YELLOW}📝 Создайте файл token.txt и поместите в него ваш токен")
            input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
            return
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка при чтении файла: {e}")
            input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
            return
    else:
        print(f"{Fore.RED}❌ Неверный выбор!")
        input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
        return
    
    # Проверяем, что токен не пустой
    if not token:
        print(f"{Fore.RED}❌ Токен не может быть пустым!")
        input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
        return
    
    # Запускаем проверку серверов
    asyncio.run(check_servers(token))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Произошла ошибка: {e}")
    
    input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
