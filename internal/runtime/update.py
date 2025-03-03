## Updater

## Configuration
Author = "Greenloop36"
RepoName = "ix-Application-Centre-Controller"

RawBaseURL = f"https://raw.githubusercontent.com/{Author}/{RepoName}/refs/heads/main"
Repository = f"https://github.com/{Author}/{RepoName}"
DownloadURL = f"https://api.github.com/repos/{Author}/{RepoName}/zipball"

## Imports
import requests
import zipfile
import os
import sys
import shutil
import json
import colorama
import pprint
from colorama import Fore, Back, Style

## Variables
Token = ""

## Functions

def ProtectedRequest(URL, DefaultHeaders: dict = None) -> tuple[bool, str | requests.Response]:
    if DefaultHeaders == None:
        DefaultHeaders = {"Accept": "application/vnd.github.v3.raw"}

    try:
        Response = requests.get(URL, headers=DefaultHeaders)
    except ConnectionError as e:
        return False, f"Connection failed. Please check your internet connection. ({e})"
    except TimeoutError as e:
        return False, f"Request timed out. ({e})"
    except requests.exceptions.InvalidSchema as e:
        return False, f"Bad Request. Check the access token.\n{e}"
    except requests.exceptions.RequestException as e:
        return False, f"Unknown error: \"{e}\". Check your internet connection."
    else:
        Success = Response.status_code >= 200 and Response.status_code < 300
        if Success:
            return True, Response
        else:
            return False, f"HTTP {Response.status_code} ({Response.reason})"

def ProtectedPost(URL, Data, DefaultHeaders: dict = None) -> tuple[bool, str | requests.Response]:
    if DefaultHeaders == None:
        DefaultHeaders = {"Accept": "application/vnd.github.v3.raw"}
    
    try:
        JSONData = json.dumps(Data)
    except:
        pass
    else:
        Data = JSONData

    try:
        Response = requests.post(URL, Data, headers=DefaultHeaders)
    except ConnectionError as e:
        return False, f"Connection failed. Please check your internet connection. ({e})"
    except TimeoutError as e:
        return False, f"Request timed out. ({e})"
    except requests.exceptions.InvalidSchema as e:
        return False, f"Bad Request. Check the access token.\n{e}"
    except requests.exceptions.RequestException as e:
        return False, f"Unknown error: \"{e}\". Check your internet connection."
    else:
        Success = Response.status_code >= 200 and Response.status_code < 300
        if Success:
            return True, Response
        else:
            return False, f"HTTP {Response.status_code} ({Response.reason})"

def CustomRequest(URL, Method: str, Data, DefaultHeaders: dict = None) -> tuple[bool, str | requests.Response]:
    print(f"\n{Method}@ {URL}")
   
    if DefaultHeaders == None:
        DefaultHeaders = {"Accept": "application/vnd.github.v3.raw"}
    
    pprint.pp(DefaultHeaders)
    pprint.pp(Data)
    
    try:
        JSONData = json.dumps(Data)
    except:
        pass
    else: 
        Data = JSONData

    try:
        Response = requests.request(url=URL, method=Method, data=Data, headers=DefaultHeaders)
        print(f"\n{Response.text}")
    except ConnectionError as e:
        return False, f"Connection failed. Please check your internet connection. ({e})"
    except TimeoutError as e:
        return False, f"Request timed out. ({e})"
    except requests.exceptions.InvalidSchema as e:
        return False, f"Bad Request. Check the access token.\n{e}"
    except requests.exceptions.RequestException as e:
        return False, f"Unknown error: \"{e}\". Check your internet connection."
    else:
        Success = Response.status_code >= 200 and Response.status_code < 300
        if Success:
            return True, Response
        else:
            return False, f"HTTP {Response.status_code} ({Response.reason})"

def IsConnectedToInternet() -> bool:
    try:
        response = requests.get("https://8.8.8.8/")
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return False    
    except Exception as e:
        return False
    else:
        return True

def GetToken():
    global Token
    return Token

def SetToken(NewToken: str) -> str:
    global Token
    Token = NewToken

    return Token

def Update(TargetDirectory: str, Branch: str = "main"):
    Url = f"{DownloadURL}/{Branch}"

    print(f"Updating from \"{Fore.LIGHTBLUE_EX}{Url}{Fore.RESET}\"...")

    ## Methods
    def PrintStatus(Message: str):
        print(f"\t| [ .. ] {Message}", end = "\r", flush = True)
    
    def PrintOk():
        print(f"\t| [ {Fore.LIGHTGREEN_EX}OK{Fore.RESET} ]")
    
    def PrintFail():
        print(f"\t| [{Fore.LIGHTRED_EX}FAIL{Fore.RESET}]")

    ## Download
    PrintStatus(f"downloading archive from branch \"{Branch}\"...")
    Success, Response = ProtectedRequest(Url)

    if Success:
        PrintOk()
    else:
        PrintFail()
        #print(f"{Fore.RED}FAIL!{Fore.RESET}")
        print(f"\nFailed to update: {Response}")
        return False
    
    ## Install
    ZipPath = f"{TargetDirectory}\\latest.zip"
    ExtractPath = f"{TargetDirectory}\\latest_version"
    
    PrintStatus(f"installing temporary files...")

    try:
        with open(ZipPath, "wb") as File:
            File.write(Response.content)
    except Exception as e:
        PrintFail()
        print(f"\nFailed to update: {e}")
        return False
    else:
        PrintOk()
    
    ## Extract
    PrintStatus(f"extracting downloaded archive...")

    try:
        with zipfile.ZipFile(ZipPath, "r") as ZipRef:
            ZipRef.extractall(ExtractPath)
    except Exception as e:
        PrintFail()
        print(f"\nFailed to update: {e}")
        return False
    else:
        PrintOk()

    ## Overwrite Settings
    PrintStatus(f"overwriting settings...")
    try:
        ## Overwrite the persistent directory
        for f in os.listdir(ExtractPath):
            if os.path.exists(f"{ExtractPath}\\{f}\\internal\\persistent"):
                for File in os.listdir(f"{TargetDirectory}\\internal\\persistent"):
                    try:
                        with open(f"{ExtractPath}\\{f}\\internal\\persistent\\{File}", "w") as NewFile:
                            with open(f"{TargetDirectory}\\internal\\persistent\\{File}", "r") as OldFile:
                                NewFile.write(OldFile.read())
                    except Exception as e:
                        pass
    except FileNotFoundError:
        PrintFail()
    except Exception as e:
        PrintFail()
        print(f"\nFailed to update: {e}")
        return False
    else:
        PrintOk()
        pass
    
    ## Patch
    PrintStatus(f"patching installation...")
    try:
        for f in os.listdir(ExtractPath):
            shutil.copytree(f"{ExtractPath}\\{f}", TargetDirectory, dirs_exist_ok=True)
                        
    except Exception as e:
        PrintFail()
        print(f"\nFailed to update: {e}")
        return False
    else:
        PrintOk()


    ## Remove
    PrintStatus(f"removing temporary files...")
    try:
        shutil.rmtree(ExtractPath)
        os.remove(ZipPath)
    except Exception as e:
        PrintFail()
        print(f"\nFailed to remove temporary files: {e}\n\nPlease remove them manually")
        return False
    else:
        PrintOk()
    

    print("\nThe update has been installed. Please restart the program.")
    os.system("pause")    
    sys.exit(0) 


def GetRawFile(Path: str, Prefix: str = "/") -> tuple[bool, str]:
    Success, Result = ProtectedRequest(f"{RawBaseURL}{Prefix}{Path}")

    if not Success:
        return False, Result
    else:
        return True, Result.text

def GetLatestVersionCode() -> str | None:
    Success, Result = GetRawFile("internal/VERSION.txt")

    if Success:
        return Result.replace("\n", "")
    else:
        return None

if __name__ == "__main__":
    colorama.init(True)
    Code = GetLatestVersionCode()
    print(f"Latest version: {Code}")

    while True:
        Choice = input(f"You can download a copy of {RepoName} via this utility. Do you wish to do so? (Y/n)\n> ").lower()

        if Choice == "y":
            from tkinter import filedialog

            print("Please select where to install the copy.")
            Path = filedialog.askdirectory(title=f"Select where to install a copy of {RepoName}")

            if Path == "":
                break
            else:
                if Update(Path) == False:
                    print("Update failed")
                
                break
        else:
            break
        
    input("Press ENTER/RETURN to exit.")