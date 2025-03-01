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
ProgramTitle = "Cryptographer"
ThisVersion = "2.1c"

## Imports
import colorama
from colorama import Fore, Back, Style
import json
import traceback

from internal.libraries.utils import UserInput

import internal.runtime.update as update

## Variables
Login = os.getlogin() # notice: this just gets your local username (to be displayed in the input prefix)
Dir = os.path.dirname(__file__)
DataFile = f"{Dir}\\internal\\persistent\\Data.json"

## Functions
    
# Out
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

    print(f"\n{Style.BRIGHT}{Fore.RED}{Name}: {str(e)}{Style.RESET_ALL}")
    print(f"\n{Style.BRIGHT}{Fore.LIGHTCYAN_EX}Stack begin{Style.NORMAL}{Fore.LIGHTBLUE_EX}\n{traceback.format_exc()}{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Stack end{Style.RESET_ALL}\n")
            

def ClearWindow():
    os.system("cls")

## Data
def Data_Set(NewData: dict) -> bool:
    try:
        with open(DataFile, "w") as File:
            File.write(json.dumps(NewData))
    except:
        return False
    else:
        return True

def Data_Read() -> dict | None:
    try:
        with open(DataFile, "r") as File:
            return json.loads(File.read())
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
            "Update Token": None
        }

        ClearWindow()
        print("Performing first time setup...")
        
        while True:
            UpdateToken = input(GetInputPrefix("Setup", "Please enter the Update Authorisation Token, or Control+C to skip."))
            # UpdateToken = input("\nPlease enter the Update Authorisation Token\nControl+C to skip\n> ")
            print("Validating...")

            update.SetUpdateToken(UpdateToken)
            Ver = update.GetLatestVersionCode()

            if Ver == None:
                print("Either the wrong token has been entered, or there is a problem with your internet connection.")
            else:
                Data["Update Token"] = UpdateToken
                print("Access is granted!")
                Pause()
                break
        
        Data_Set(Data)
        ClearWindow()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        ExceptionWithTraceback(e)
        Quit(f"Fatal error during setup!")


## Internal Commands
class Container_Commands:
    def encrypt(_, Query: str = ""):
        if Query in ("", None):
            try:
                Query = input(GetInputPrefix("encrypt", "Please enter a query to encrypt"))
            except KeyboardInterrupt:
                return
        
        try:
            Result = crypt.Encode(Query)
        except Exception as e:
            Error(f"Failed to encode the query \"{Query}\"! ({str(e)})")
        else:
            clipboard.copy(Result)

            print("=========== RESULT ===========")
            print(Result)
            print("==============================")
    
    def decrypt(_, Query: str = ""):
        if Query in ("", None):
            try:
                Query = input(GetInputPrefix("decrypt", "Please enter a query to encrypt:"))
            except KeyboardInterrupt:
                return
        
        try:
            Result = crypt.Decode(Query)
        except Exception as e:
            Error(f"Failed to decode the query \"{Query}\"!\nHave you properly copied/pasted the message? ({str(e)})")
        else:
            clipboard.copy(Result)
            
            print("=========== RESULT ===========")
            print(Result)
            print("==============================")
    
    def auto(*_):
        Notice("Entering automatic mode. Paste in text and it will be automatically encrypted or decrypted. Press Control+C to exit this mode.")
        while True:
            try:
                Query = input(GetInputPrefix("auto", "Enter a query for automatic encryption/decryption"))
            except KeyboardInterrupt:
                print()
                return
            
            if Query == "" or Query.startswith(" "):
                continue

            try:
                Enc = crypt.Encode(Query)
            except Exception as e:
                Enc = None
            
            try:
                Dec = crypt.Decode(Query)
            except Exception as e:
                Dec = None

            if Enc == None and Dec == None:
                Error("Malformed input. Nothing was encoded or decoded.")
            elif Enc != None and Dec == None: # Only encryption returned a result
                print(f"{Fore.CYAN}Encryption{Fore.RESET}\n{Enc}\n")
                clipboard.copy(Enc)
            else: # Decryption returned a result
                print(f"{Fore.BLUE}Decryption{Fore.RESET}\n{Dec}\n")
                clipboard.copy(Dec)
    
    def init(*_):
        Warning("This will reset your update token. Only do this if a new update token is available.")
        if UserInput.YesNo("Do you wish to continue?"):
            FirstSetup()
    
    def prepareforpush(*_):
        Warning("This is a developer-only command, and will reset most settings.")
        if UserInput.YesNo("Do you wish to continue?"):
            Data_Set({})
    

    def update(*_):
        print("Preparing to update...")
        Latest = update.GetLatestVersionCode()

        if Latest == None:
            return Error("Could not get latest version. Check your update token.")
        elif Latest == ThisVersion:
            Warning(f"You are already using the latest version available, {Fore.LIGHTGREEN_EX}{ThisVersion}{Fore.RESET}.")

            if not UserInput.YesNo("Do you want to update anyway?"):
                return
        else:
            print(f"You are about to upgrade to the latest version, {Fore.LIGHTGREEN_EX}{ThisVersion}{Fore.RESET}.")
            if not UserInput.YesNo("Do you want to continue?"):
                return

        ClearWindow()
        update.Update(Dir)

## Runtime
Commands = Container_Commands()

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
        UpdateToken = Data["Update Token"]
    except:
        UpdateToken = None

    update.SetUpdateToken(UpdateToken)
    
    LatestVer = update.GetLatestVersionCode()

    ## Check data
    Data = Data_Read()
    if ( ## Ensure that the update token is valid, else prompt to first setup
        Data == None 
        or 
        (
            "Update Token" in Data
            and
            (Data["Update Token"] == "" or Data["Update Token"] == None)
            )
        or
        LatestVer == None
    ):
        FirstSetup()
        

    ## Greeting
    ClearWindow()
    print(f"Cryptographer [Version {ThisVersion}]")
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

    if ThisVersion != LatestVer and LatestVer != None:
        Notice(f"An update is available! Run \"{Fore.BLUE}update{Fore.RESET}\" to download the latest version. ({Fore.LIGHTRED_EX}{ThisVersion}{Fore.RESET} -> {Fore.GREEN}{LatestVer}{Fore.RESET})")
    
    # if Data.get("Update Token", None) == None:
    #     Warning(f"Missing update token! Run the \"{Fore.BLUE}init{Fore.RESET}\" command or restart the program to enter one.")

    if LatestVer == None:
        Warning("Failed to get latest update! Please check your internet connection or update token.")

    ## Set the updater's update token
    Data = Data_Read() or {}
    update.SetUpdateToken(Data.get("Update Token", None))

    ## Command line loop
    while True:
        try:
            Query = input(GetInputPrefix())
        except KeyboardInterrupt:
            Quit()
        else:
            print()
            Valid, Command, Params = ParseInput(Query)

            if not Valid or Command == "":
                continue

            ## Get the method
            Method = getattr(Commands, Command, None)

            if callable(Method):
                try:
                    Method(Params)
                except Exception as e:
                    CustomException(f"\nAn exception ocurred whilst running the command \"{Command}\"!")
                    ExceptionWithTraceback(e)
            else:
                CustomException(f"\"{Command}\" is not recognised as an internal command.")

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

            CustomException(f"\nA fatal error ocurred during runtime! The program will now exit. See details below.\n\n")
            ExceptionWithTraceback(e)
            Pause()
    else:
        ClearWindow()
        Warning("Errors will be uncaught!\n")
        Pause()
        main()
    