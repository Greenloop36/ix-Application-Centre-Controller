## Coloured Output

from colorama import Fore, Back, Style
import traceback as tb

__DEMOTEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam posuere."

__all__ = ["error", "success", "notice", "warn", "exception", "traceback", "info", "init"]

## Methods
def _CreatePrefix(Prefix: str = None):
    if Prefix != None:
        Prefix = f" {Style.BRIGHT}{Fore.WHITE}{Back.BLUE} {Prefix} {Style.RESET_ALL} "
    else:
        Prefix = " "
    return Prefix

def info(Message: str, Prefix: str = None):
    print(f"{Style.BRIGHT}{Fore.BLUE}info{Style.RESET_ALL}:{_CreatePrefix(Prefix)}{Message}")

def error(Message: str, Prefix: str = None):
    print(f"{Style.BRIGHT}{Fore.RED}error{Style.RESET_ALL}:{_CreatePrefix(Prefix)}{Message}")
    # print(Style.BRIGHT + Fore.RED + "error" + Style.RESET_ALL + ": " + str(Message))

def success(Message: str, Prefix: str = None):
    print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}success{Style.RESET_ALL}:{_CreatePrefix(Prefix)}{Message}")
    # print(Fore.LIGHTGREEN_EX + "success" + Fore.RESET + ": " + str(Message))

def notice(Message: str, Prefix: str = None):
    print(f"{Style.BRIGHT}{Fore.MAGENTA}notice{Style.RESET_ALL}:{_CreatePrefix(Prefix)}{Message}")
    # print(Style.BRIGHT + Fore.MAGENTA + "notice" + Style.RESET_ALL + ": " + str(Message))

def warn(Message: str, Prefix: str = None):
    print(f"{Style.BRIGHT}{Fore.YELLOW}warning{Style.RESET_ALL}:{_CreatePrefix(Prefix)}{Message}")

def exception(Message: str):
    print(Fore.LIGHTRED_EX + str(Message) + Fore.RESET)

def traceback(e):
    Name = type(e).__name__

    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.RED} {Name} {Back.RESET}{Fore.RED}: {str(e)}{Style.RESET_ALL}")
    print(f"\n{Style.BRIGHT}{Fore.LIGHTCYAN_EX}Stack begin{Style.NORMAL}{Fore.LIGHTBLUE_EX}\n{tb.format_exc()}{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Stack end{Style.RESET_ALL}\n")

## Demo
def __demonstration():
    error(__DEMOTEXT)
    success(__DEMOTEXT)
    notice(__DEMOTEXT)
    warn(__DEMOTEXT)
    exception(__DEMOTEXT)

    notice(__DEMOTEXT, "meow")

    try:
        int(__DEMOTEXT)
    except Exception as e:
        traceback(e)


if __name__ == "__main__":
    from colorama import init
    init(True)
    __demonstration()