## Init
from internal.runtime.init import main as ProgramInit
import sys
import os
if not ("!noinit" in sys.argv):
    if ProgramInit() != True:
        input("Init failed. Press RETURN to exit.")
        sys.exit(1)
else:
    os.system("cls")
    print("starting...")

os.chdir("C:/")


## Configuration
ProgramTitle = "ApplicationCentreController"
ThisVersion = "1.0"

## Imports
import colorama
from colorama import Fore, Back, Style
import json
import traceback
import ctypes

from internal.libraries.utils import UserInput
import internal.runtime.gui as Application
import internal.runtime.update as update

## Variables
Login = os.getlogin() # notice: this just gets your local username (to be displayed in the input prefix)
Dir = os.path.dirname(__file__)
DataFile = f"{Dir}\\internal\\persistent\\Data.json"

## Functions
    
# Out
def toggle_console(visible):
    console_window = ctypes.windll.kernel32.GetConsoleWindow()
    if console_window:
        ctypes.windll.user32.ShowWindow(console_window, 1 if visible else 0)

def Error(Message: str):
    print(Style.BRIGHT + Fore.RED + "error" + Style.RESET_ALL + ": " + str(Message))

def PrintSuccess(Message: str):
    print(Fore.LIGHTGREEN_EX + "success" + Fore.RESET + ": " + str(Message))

def Notice(Message: str):
    print(Style.BRIGHT + Fore.MAGENTA + "notice" + Style.RESET_ALL + ": " + str(Message))

def Warning(Message: str):
    print(Style.BRIGHT + Fore.YELLOW + "warning" + Fore.RESET + Style.RESET_ALL + ": " + str(Message))

def CustomException(Message: str):
    print(Fore.LIGHTRED_EX + str(Message) + Fore.RESET)

def ExceptionWithTraceback(e):
    Name = type(e).__name__

    print(f"\n{Style.BRIGHT}{Fore.WHITE}{Back.RED} {Name} {Back.RESET}{Fore.RED}: {str(e)}{Style.RESET_ALL}")
    print(f"\n{Style.BRIGHT}{Fore.LIGHTCYAN_EX}Stack begin{Style.NORMAL}{Fore.LIGHTBLUE_EX}\n{traceback.format_exc()}{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Stack end{Style.RESET_ALL}\n")
            

def ClearWindow():
    os.system("cls")

## Data
def Data_Set(NewData: dict) -> bool:
    try:
        if not os.path.exists(DataFile):
            with open(DataFile, "x") as File:
                File.write("")
            
        with open(DataFile, "w") as File:
            File.write(json.dumps(NewData))
    except:
        return False
    else:
        return True

def Data_Read() -> dict | None:
    try:
        with open(DataFile, "r") as File:
            return json.loads(File.read()) or {}
    except Exception as e:
        # Warning(f"Failed to read data: {e}")
        # Pause()
        return None

# Other
def init():
    colorama.init()

def GetInputPrefix(Process: str = "Main", Instruction: str = None) -> str:
    if Instruction != None:
        Instruction = f"{Fore.RESET}: {Fore.LIGHTBLUE_EX}{Instruction}\n{Fore.BLUE}> {Fore.RESET}"
    else:
        Instruction = f"\n{Fore.MAGENTA}$ {Fore.RESET}"

    return f"\n{Fore.GREEN}{Login}@{ProgramTitle}{Fore.RESET} {Style.DIM}~{Style.RESET_ALL} {Fore.YELLOW}{Process}{Instruction}"

def ParseInput(Query: str) -> tuple[bool, str, str]:
    try:
        Parts = Query.split(" ", 1)
        Command = Parts[0]
        Params = len(Parts) > 1 and Parts[1] or None
    except:
        return False, None, None
    else:
        return True, Command, Params

def Pause():
    os.system("pause")

def Quit(Message: str | None = None):
    if Message:
        CustomException(f"\n{Message}")
        print("\n\nThe program will now exit.")
        Pause()
        sys.exit(0)
    else:
        CustomException("\nQuitting...")
        sys.exit(0)

def FirstSetup():
    try:
        Data = {
            "Commit Token": None,
            "Username": None,
            "Email": None
        }

        ClearWindow()
        Notice("Performing first time setup:\nControl+C to skip (Will result in read-only access)\n\n")
        
        while True:
            Username = input(GetInputPrefix("Setup", "Enter your username. This is used in the commit message."))
            Email = input(GetInputPrefix("Setup", "Enter your email. This is used in the commit message."))
            Token = input(GetInputPrefix("Setup", "Please enter the Commit Access Token, or Control+C to skip."))
            # UpdateToken = input("\nPlease enter the Update Authorisation Token\nControl+C to skip\n> ")

            update.SetToken(Token)

            Data["Commit Token"] = Token
            Data["Email"] = Email
            Data["Username"] = Username
            break
        
        Success = Data_Set(Data)
        if not Success:
            Warning("Failed to save data")
            Pause()

        ClearWindow()
    except KeyboardInterrupt:
        Warning("You will only have READ access, as a token has not been given.")
        Pause()

        pass
    except Exception as e:
        ExceptionWithTraceback(e)
        Quit(f"Fatal error during setup!")



## Runtime

def main():

    ## Init
    ClearWindow()
    print("setting up...")
    Data = Data_Read()

    init()

    ## Retrieve latest version code 
    ClearWindow()
    print("checking for updates...")

    try:
        UpdateToken = Data["Commit Token"]
    except:
        UpdateToken = None

    update.SetToken(UpdateToken)
    
    LatestVer = update.GetLatestVersionCode()

    ## Check data
    Data = Data_Read() or {}
    
    if Data.get("Commit Token", None) == None:
        FirstSetup()
        

    ## Greeting
    ClearWindow()
    print(f"{ProgramTitle} [Version {ThisVersion}]")
    print(f"Control+C to exit\n")

    ## Ensure that file version code & current version code (stored in Configuration) are the same
    try:
        Ver = open(f"{Dir}\\internal\\VERSION.txt", "r")
        if Ver.readable():
            FileVer = Ver.read().replace("\n", "")
            if FileVer != ThisVersion:
                Warning(f"Mismatch between program version and file version! {ThisVersion = } != {FileVer = }")
        Ver.close()
    except Exception as e:
        Warning(f"Failed to read {Dir}\\internal\\VERSION.txt file: {e}")
    
    ## Check for updates & refresh the version code (if unauthorised, it will be blank)
    LatestVer = update.GetLatestVersionCode()
    ShouldUpdate = False

    if ThisVersion != LatestVer and LatestVer != None:
        ShouldUpdate = True
        
    # if Data.get("Commit Token", None) == None:
    #     Warning(f"Missing Commit Token! Run the \"{Fore.BLUE}init{Fore.RESET}\" command or restart the program to enter one.")

    if LatestVer == None:
        Warning("Failed to get latest update! Please check your internet connection or Commit Token.")

    ## Set the updater's Commit Token
    Data = Data_Read() or {}
    update.SetToken(Data.get("Commit Token", None))

    ## Main loop
    if ShouldUpdate:
        print(f"Update available: You can to upgrade to the latest version, {Fore.LIGHTGREEN_EX}{ThisVersion}{Fore.RESET}.")
        if UserInput.YesNo("Do you want to continue?"):
            update.Update(Dir)
    
    try:
        toggle_console(False)
        Application.main(Data_Read(), DataFile)
        ExitCode = Application.GetExitCommand()
        
        if ExitCode:
            toggle_console(True)

            if ExitCode == "update":
                if UserInput.YesNo(f"Are you sure you want to install the latest version, {Fore.LIGHTGREEN_EX}{ThisVersion}{Fore.RESET}?"):
                    update.Update(Dir)


    except Exception as e:
        toggle_console(True)

        CustomException(f"\nA fatal error ocurred during runtime! The program will now exit. See details below.")
        ExceptionWithTraceback(e)
        Pause()
    

if __name__ == "__main__":
    CatchErrors = True ## Debug flag

    if CatchErrors:
        try:
            main()
        except KeyboardInterrupt:
            Quit()
        except EOFError:
            Quit()
        except Exception as e:
            if e == "" or e == None:
                e = "Unknown exception"

            CustomException(f"\nA fatal error ocurred during runtime! The program will now exit. See details below.")
            ExceptionWithTraceback(e)
            Pause()
    else:
        ClearWindow()
        Warning("Errors will be uncaught!\n")
        Pause()
        main()
    