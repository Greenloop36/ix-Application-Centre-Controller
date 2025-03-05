from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from datetime import datetime

from . import update
from ..libraries import output as out

import webbrowser as browser
import os
import requests
import json
import base64
import time

## Configuration
DefaultPadding = 10
ProgramTitle = "Application Centre Controller"
API = "https://api.github.com/repos/Greenloop36/ix-ApplicationCentre_Status/contents"
DownloadFilePath = "https://raw.githubusercontent.com/Greenloop36/ix-ApplicationCentre_Status/main/"
STATUS_REPO_URL = "https://github.com/Greenloop36/ix-ApplicationCentre_Status"
CONTROLLER_REPO_URL = "https://github.com/Greenloop36/ix-Application-Centre-Controller"

## init
Root = None

## Variables
ExitCommand = None
UserData = {}
Token = None
DataFile = ""
RefreshDebounce = 0
CurrentRow = 0
CurrentData = {}
ContentFrame = None
HeaderFont = None

## Methods
# def TokenWindow():
#     Window = Toplevel()
#     HeaderFont = font.Font(size = 16, weight = "bold")

#     Header = ttk.Frame(Window)
#     Header.grid(sticky="w")
    
#     ttk.Label(Header, font=HeaderFont)
#     ttk.Label(Header, text="Commit Access Token", font=HeaderFont, anchor = "w").grid(column=0, row=0, sticky="w", padx=(DefaultPadding, 30),pady=(DefaultPadding, 0))


#     EntryFrame = ttk.Frame(Window)
#     EntryFrame.grid(sticky="w")

#     TokenEntry = ttk.Entry(EntryFrame, show="*", textvariable=TokenVariable, width=75)
#     TokenEntry.grid(sticky="nwse", padx=(DefaultPadding, DefaultPadding),pady=(DefaultPadding, 0))


#     ButtonsFrame = ttk.Frame(Window)
#     ButtonsFrame.grid(sticky="e")

#     CloseButton = ttk.Button(ButtonsFrame, text="Close", command=Window.destroy)
#     CloseButton.grid(sticky="e", padx=(DefaultPadding, DefaultPadding),pady=(DefaultPadding, DefaultPadding))

#     Window.mainloop()

def unix_to_relative(unix_timestamp: int) -> str:
    # Get the current time as a Unix timestamp
    current_time = datetime.now().timestamp()

    # Calculate the difference in seconds
    difference = current_time - unix_timestamp

    # Convert the difference into a human-readable format
    if difference < 60:  # Less than a minute
        return f"{int(difference)} seconds ago"
    elif difference < 3600:  # Less than an hour
        minutes = int(difference // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif difference < 86400:  # Less than a day
        hours = int(difference // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:  # More than a day
        days = int(difference // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"

def TkObjectsToDict(Target: dict) -> dict:
    Result = {}

    for Index, Object in Target.items():
        if isinstance(Object, dict):
            Result[Index] = TkObjectsToDict(Object)
        else:
            if isinstance(Object, ttk.Checkbutton):
                Result[Index] = Object.instate(["selected"])
            else:
                Result[Index] = Object.get()
    
    return Result

def GetStatus() -> tuple[bool, dict | str]:
    URL = f"{API}Status.json"
    Success, Result = update.ProtectedRequest(URL)

    if Success:
        try:
            Data = Result.json()
            # print(Data)
            # Data = base64.b64decode(Data["content"]).decode()
            # Data = json.loads(Data)
        except requests.JSONDecodeError:
            return False, "Could not decode JSON! (1)"
        except json.decoder.JSONDecodeError:
            return False, "Could not decode JSON! (2)"
        except Exception as e:
            return False, "Failed to decode base64 contents!"
        else:
            Ratelimit_remaining = int(Result.headers["x-ratelimit-remaining"])
            Ratelimit_used = int(Result.headers["x-ratelimit-used"])
            Ratelimit_refresh = int(Result.headers["x-ratelimit-reset"])

            if 20 >= Ratelimit_remaining:
                messagebox.showwarning(ProgramTitle, f"WARNING: A ratelimit will be imposed shortly in {Ratelimit_remaining} more requests.\nThis will expire in {unix_to_relative(Ratelimit_refresh)}.")
            
            return True, Data
    else:
        out.warn(f"GET to {URL} failed: {Result.status_code} ({Result.reason})", "GetStatus")
        return False, f"GET failed: HTTP {Result.status_code} ({Result.reason})"

def SetStatus(Data: dict) -> tuple[bool, str | None]:
    if not "Username" in UserData:
        out.error("aborting commit: user not authenticated", "SetStatus")
        return False, "Authenticate with your username and email."

    HEADERS = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'token {Token}',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
    }

    response = requests.get(f"{API}/Status.json", headers=HEADERS)

    if response.status_code != 200:
        out.error(f"fetch failed: {response.status_code} ({response.reason})", "SetStatus")
        return False, f"Failed to fetch file SHA: HTTP {response.status_code} ({response.reason})"
    
    ResponseData = response.json()

    sha = ResponseData['sha']
    CurrentStatusData: str = ResponseData["content"]

    # try:
    #     CurrentStatusData = base64.b64decode(CurrentStatusData).decode()
    # except:
    #     CurrentStatusData = None

    ## Convert dict to JSON (str)
    try:    
        Data: str = json.dumps(Data)
    except Exception as e:
        out.error(f"Failed to convert data to JSON", "SetStatus")
        out.traceback(e)

        return False, "Could not convert to JSON!"

    ## Encode with base64, as github requires that format
    try:
        Data = base64.b64encode(Data.encode("utf-8")).decode()
    except Exception as e:
        # print(f"[SetStatus]: b64encode failed: {e}")
        out.error(f"Failed to encode JSON to base64", "SetStatus")
        out.traceback(e)

        return False, "Could not encode to Base64!"
    
    if CurrentStatusData.replace("\n", "") == Data:
        out.warn("Aborting SetStatus: no changes were made.", "SetStatus")
        return False, "No changes to commit."
    
    ## Prepare data
    BODY = {
        "message": f"{UserData['Username']} submitted data.",
        "committer": {
            "name": UserData["Username"],
            "email": UserData["Email"]
        },
        "content": Data,
        "sha": sha  # Include the SHA of the file
    }

    ## Commit
    out.info("committing...", "SetStatus")
    return update.CustomRequest(f"{API}/Status.json", "PUT", BODY, HEADERS)

def ClearFrame(ContentFrame):
    for widget in ContentFrame.winfo_children():
        widget.destroy()

def CreateObjectsForDict(Dictionary: dict, Container, Indent: int = 0, SaveTo: dict = CurrentData):
    global CurrentRow

    for Index, Value in Dictionary.items():
        CurrentRow += 1
        Type = type(Value).__name__
        # Variable = None

        if Indent != 0:
            Frame(Container, bg="black", width=1).grid(row=CurrentRow, column=0, sticky="nwse", padx=(DefaultPadding, DefaultPadding))

        ttk.Label(Container, text=Index, anchor="w").grid(row=CurrentRow, column=1, sticky="nwse", padx=(Indent, DefaultPadding), pady=(0, DefaultPadding))

        # def Update():
        #     CurrentData[]

        if Type == "str":
            Object = ttk.Entry(Container)
            Object.delete(0, END)
            Object.insert(0, Value)

        elif Type == "bool":
            Object = ttk.Checkbutton(Container)
            Object.state(['!alternate'])

            if Value == True:
                Object.state(["selected"])
            else:
                Object.state(["!selected"])

        elif Type == "dict":
            SaveTo[Index] = {}
            SaveTo[Index] = CreateObjectsForDict(Value, Container, DefaultPadding + Indent, SaveTo[Index])
            continue
        
        Object.grid(row=CurrentRow, column=2, sticky="e", pady=(0, DefaultPadding))
        SaveTo[Index] = Object
    

    return SaveTo
        

def RefreshWindow(Override: bool = False) -> bool:
    global ContentFrame, CurrentRow, RefreshDebounce, CurrentData

    if RefreshDebounce > time.time() and not Override:
        out.warn(f"Refresh rejected: debounce ({(RefreshDebounce - time.time()):.2f}s remaining)", "RefreshWindow")
        return messagebox.showwarning("Warning", "Please wait before sending another request.")
    else:
        RefreshDebounce = time.time() + 5

    CurrentRow = 0

    ClearFrame(ContentFrame)
    Root.update()

    out.info("refreshing...", "RefreshWindow")
    GetSuccess, StatusData = GetStatus()

    if not GetSuccess:
        out.error(f"refresh failed: {StatusData}", "RefreshWindow")
        messagebox.showerror("Error", f"Could not retrieve status information: {StatusData}")

        return
    else:
        out.success("refreshed", "RefreshWindow")
        # print(GetSuccess, StatusData)

    CurrentData = CreateObjectsForDict(StatusData, ContentFrame)

def OnSubmit():
    Target = TkObjectsToDict(CurrentData)

    out.info("attempting commit...", "OnSubmit")
    Success, Result = SetStatus(Target)
    # RefreshWindow(True)

    if Success:
        out.success("Commit successful.", "OnSubmit")
        return messagebox.showinfo(ProgramTitle, "Successfully updated centre status.")
    else:
        out.error(f"Commit failed: {Result}", "OnSubmit")
        return messagebox.showerror(ProgramTitle, f"Failed to commit: {Result}")

def InitData():
    if not os.path.exists(DataFile):
        out.error(f"Cannot reset (data file does not exist)", "InitData")
        return messagebox.showerror(ProgramTitle, "error: Data file does not exist. Try reinstalling the app.")

    try:
        if not messagebox.askyesno(ProgramTitle, "Are you sure you want to reset your user data?"): return

        with open(DataFile, "w") as File:
            File.write("{}")
    except Exception as e:
        out.error(f"Cannot reset (file system error)", "InitData")
        out.traceback(e)

        return messagebox.showerror(ProgramTitle, f"error: Failed to write to file ({e})")
    else:
        out.success("reset complete", "InitData")
        return messagebox.showinfo(ProgramTitle, "User data was reset.\nRestart the program to perform first-time setup again.")

def ExitWithCommand(Root: Tk, Command: str):
    global ExitCommand
    ExitCommand = Command

    out.info(f"exiting with status \"{Command}\"", "ExitWithCommand")

    Root.destroy()

def GetExitCommand():
    return ExitCommand

def main(Data, DataFilePath):
    global ContentFrame, Root, Token, UserData, DataFile
    UserData = Data
    DataFile = DataFilePath

    ## UI
    Root = Tk()
    Root.title(ProgramTitle)
    Root.resizable(False, False)
    Token = update.GetToken()
    Root.option_add('*tearOff', FALSE)

    # Menubar
    Menubar = Menu(Root)
    Root["menu"] = Menubar
    Menu_File = Menu(Menubar)
    Menu_Edit = Menu(Menubar)
    Menu_View = Menu(Menubar)
    Menu_View_Repo = Menu(Menubar)

    Menubar.add_cascade(menu=Menu_File, label="File")
    Menu_File.add_command(label="Repair/update installation", command=lambda: ExitWithCommand(Root, "update"))
    Menu_File.add_separator()
    Menu_File.add_command(label="Exit and view log", command=lambda: ExitWithCommand(Root, "quit_to_terminal"))
    Menu_File.add_command(label="Exit", command=Root.destroy)

    Menubar.add_cascade(menu=Menu_Edit, label="Edit")
    Menu_Edit.add_command(label="Initialise user data", command=InitData)

    Menubar.add_cascade(menu=Menu_View, label="View")
    Menu_View.add_cascade(menu=Menu_View_Repo, label="Open Repositories...")
    Menu_View_Repo.add_command(label="Status", command=lambda: browser.open_new_tab(STATUS_REPO_URL))
    Menu_View_Repo.add_command(label="Controller", command=lambda: browser.open_new_tab(CONTROLLER_REPO_URL))

    # Header
    HeaderFont = font.Font(size = 16, weight = "bold")
    HeaderFrame = ttk.Frame(Root)
    HeaderFrame.grid(sticky="w")
    ttk.Label(HeaderFrame, text=ProgramTitle, font=HeaderFont, anchor = "w").grid(column=0, row=0, sticky="w", padx=(DefaultPadding, 30),pady=(DefaultPadding, 0))
    ttk.Label(HeaderFrame, text="Remote control interface", anchor = "w").grid(column=0, row=1, sticky="w", padx=(DefaultPadding, 30), pady=(0, DefaultPadding))

    # Content
    ContentFrame = ttk.Frame(Root, padding=10)
    ContentFrame.grid(sticky="nwse")

    RefreshWindow()

    if not update.CheckToken(Token) and Token != None:
        out.warn(f"The token provided to the program, {Token}, may be invalid.", "main")
        messagebox.showwarning(ProgramTitle, f"The provided token,\n\n{Token}\n\nmay not be valid! Please check it and try again.\nSelect Edit > Initialise... to reset your token.")
    elif Token == None:
        out.warn("No token was provided: committing not possible.")

    # Buttons
    ButtonsFrame = ttk.Frame(Root, padding = 10)
    ButtonsFrame.grid(sticky="E")
    ttk.Button(ButtonsFrame, text="Refresh", command=RefreshWindow).grid(column=1, row=0, sticky="E", padx=(0, DefaultPadding))
    SubmitButton = ttk.Button(ButtonsFrame, text="Submit", command=OnSubmit)
    SubmitButton.grid(column=2, row=0, sticky="E")

    ## Token
    if update.GetToken() == "":
        # TokenWindow()
        pass

    ## Run
    Root.mainloop()

## Runtime
if __name__ == "__main__":
    out.init(True)
    main()