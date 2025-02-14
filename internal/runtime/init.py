## Initialisation

## Configuration
RequiredModules = ["colorama", "requests"]

## Imports
import subprocess
import importlib.util
import sys
import os
import ensurepip

## Variables
Modules = sys.modules


## Functions
def InstallModule(Name: str) -> tuple[bool, str, int]:
    result = subprocess.run(['cmd', '/c', f'pip install {Name}'], shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return True, result.stdout, result.returncode
    else:
        return False, result.stderr, result.returncode

# def IsModuleInstalled(Name: str) -> bool:
#     a = None
#     Installed: bool = None

#     try:
#         a = __import__(Name)
#     except ModuleNotFoundError:
#         Installed = False
#     else:
#         Installed = True
#     finally:
#         a = None
#         return Installed

def IsModuleInstalled(Name: str) -> bool:
    if Name in Modules:
        return True
    elif importlib.util.find_spec(Name) != None:
        return True
    else:
        return False

def ClearWindow() -> None:
    os.system("cls")

def Pause() -> None: # Wait for a key press
    os.system("pause")

def Quit(Message: str | None = None):
    if Message:
        print(f"\n{Message}")
    
    print("\n\nThe program will now exit.")
    Pause()
    sys.exit(0)


## Runtime
def main() -> bool | None:
    ## Variables
    ModulesToInstall: list[str] = []

    ## Check for Pip
    print("checking for pip...", flush=True)
    PipInstalled = IsModuleInstalled("pip")

    if PipInstalled:
        print("\t| Pip is installed")
    else:
        print("\t| Pip is not installed!")

    ## Install Pip
    if not PipInstalled:
        print("\nconfiguring pip...", flush=True)

        print("\t| bootstrapping pip:", end = "", flush=True)
        ensurepip.bootstrap()

        print("\t| upgrading pip:", end = "", flush=True)
        result = subprocess.run(['cmd', '/c', f'python -m pip install --upgrade pip'], shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print("pip was installed successfully!")
            Quit("Please restart the program.")

    ## Check if dependencies are installed
    print("\nchecking required dependencies...")
    for i in RequiredModules:
        print(f"\t| \"{i}\":", end = " ", flush=True)
        Installed = IsModuleInstalled(i)

        if not Installed:
            ModulesToInstall.append(i)
            print("Missing", flush=True)
        else:
            print("OK", flush=True)
    
    print()
    
    ## Install the required dependencies
    if len(ModulesToInstall) > 0:
        print("installing required dependencies, this may take some time...")
        
        for i in ModulesToInstall:
            print(f"\t| \"{i}\":", end=" ", flush=True)
            Success, Result, ReturnCode = InstallModule(i)

            if Success:
                print("OK", flush=True)
            else:
                print("FAILED!", flush=True)
                Quit(f"The module \"{i}\" failed to install. Please try again.\n\n{Result}\n\nExit code: {str(ReturnCode)}")

        Quit("The required modules have now been installed. Please restart the program.")

    print("waiting for MAIN to continue...")
    return True
    
if __name__ == "__main__":
    main()
    Pause()