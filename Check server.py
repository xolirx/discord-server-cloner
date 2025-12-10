import aiohttp
import asyncio
from colorama import init, Fore, Back, Style

init(autoreset=True)

def print_banner():
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.MAGENTA}{Back.BLACK}        🚀 Discord Server Checker Pro")
    print(f"{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.YELLOW}👤 Автор: {Fore.WHITE}zlafik")
    print(f"{Fore.YELLOW}📞 Discord: {Fore.WHITE}zlafik")
    print(f"{Fore.YELLOW}📱 Telegram: {Fore.WHITE}@zlafik")
    print(f"{Fore.YELLOW}📢 Telegram Channel: {Fore.WHITE}@biozlafik")
    print(f"{Fore.CYAN}{'═' * 60}")

async def check_servers(token):
    headers = {'Authorization': token}
    
    async with aiohttp.ClientSession() as session:
        print(f"\n{Fore.CYAN}🔍 Проверяем токен...")
        try:
            async with session.get('https://discord.com/api/v9/users/@me', headers=headers) as r:
                if r.status == 200:
                    user = await r.json()
                    print(f"{Fore.GREEN}✅ ТОКЕН РАБОЧИЙ!")
                    print(f"{Fore.CYAN}👤 Пользователь: {Fore.WHITE}{user['username']}#{user['discriminator']}")
                    print(f"{Fore.CYAN}🆔 ID пользователя: {Fore.WHITE}{user['id']}")
                    print(f"{Fore.CYAN}📧 Email: {Fore.WHITE}{user.get('email', 'Скрыт')}")
                    
                    print(f"\n{Fore.CYAN}📂 Получаем список серверов...")
                    async with session.get('https://discord.com/api/v9/users/@me/guilds', headers=headers) as guilds_r:
                        if guilds_r.status == 200:
                            guilds = await guilds_r.json()
                            print(f"{Fore.GREEN}✅ Найдено серверов: {len(guilds)}")
                            
                            print(f"\n{Fore.CYAN}📋 Список серверов:")
                            print(f"{Fore.CYAN}{'─' * 60}")
                            
                            for i, guild in enumerate(guilds, 1):
                                guild_id = guild['id']
                                guild_name = guild['name']
                                permissions = guild.get('permissions', 0)
                                is_admin = (int(permissions) & 0x8) == 0x8
                                admin_badge = f"{Fore.RED} [ADMIN]" if is_admin else ""
                                
                                print(f"{Fore.WHITE}   {i:2d}. 🏠 {guild_name}{admin_badge}")
                                print(f"{Fore.GRAY}       🆔 ID: {guild_id}")
                                if i < len(guilds):
                                    print(f"{Fore.DARKBLUE}       {'─' * 40}")
                            
                            print(f"{Fore.CYAN}{'─' * 60}")
                            print(f"\n{Fore.GREEN}🎉 Все сервера загружены успешно!")
                                
                        else:
                            print(f"{Fore.RED}❌ Не удалось получить список серверов: {guilds_r.status}")
                else:
                    print(f"{Fore.RED}❌ Токен невалидный: {r.status}")
        except aiohttp.ClientConnectionError:
            print(f"{Fore.RED}❌ Ошибка подключения к Discord!")
            return
        except asyncio.TimeoutError:
            print(f"{Fore.RED}❌ Таймаут подключения!")
            return
        except Exception as e:
            print(f"{Fore.RED}❌ Неожиданная ошибка: {e}")
            return

def main():
    print_banner()
    
    print(f"\n{Fore.YELLOW}🔐 Выберите способ ввода токена:")
    print(f"{Fore.CYAN}1. {Fore.WHITE}Ввести токен вручную")
    print(f"{Fore.CYAN}2. {Fore.WHITE}Использовать токен из файла")
    print(f"{Fore.CYAN}3. {Fore.WHITE}Инструкция по получению токена")
    
    choice = input(f"\n{Fore.YELLOW}[?] Выберите вариант (1/2/3): {Fore.WHITE}").strip()
    
    token = ""
    
    if choice == "1":
        print(f"\n{Fore.YELLOW}📝 Введите ваш Discord токен:")
        print(f"{Fore.RED}⚠️  Внимание: Токен будет виден при вводе!")
        token = input(f"{Fore.YELLOW}[?] Токен: {Fore.WHITE}").strip()
        
    elif choice == "2":
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
    elif choice == "3":
        print(f"\n{Fore.CYAN}📖 ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ ТОКЕНА:")
        print(f"{Fore.WHITE}1. Откройте Discord в браузере")
        print(f"{Fore.WHITE}2. Нажмите F12 → Вкладка 'Network'")
        print(f"{Fore.WHITE}3. Обновите страницу (F5)")
        print(f"{Fore.WHITE}4. Найдите любой запрос к discord.com")
        print(f"{Fore.WHITE}5. В Headers найдите 'Authorization'")
        print(f"{Fore.WHITE}6. Скопируйте токен (начинается с букв)")
        print(f"{Fore.YELLOW}⚠️  Никому не передавайте ваш токен!")
        input(f"\n{Fore.CYAN}Нажмите Enter для возврата...")
        main()
        return
    else:
        print(f"{Fore.RED}❌ Неверный выбор!")
        input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
        return
    
    if not token:
        print(f"{Fore.RED}❌ Токен не может быть пустым!")
        input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")
        return
    
    asyncio.run(check_servers(token))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Произошла ошибка: {e}")
    
    input(f"\n{Fore.CYAN}Нажмите Enter для выхода...")