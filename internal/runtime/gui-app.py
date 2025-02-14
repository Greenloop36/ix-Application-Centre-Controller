from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
import update
import json
import base64
import time

## Configuration
DefaultPadding = 10
ProgramTitle = "Application Centre Controller"
API = "https://api.github.com/repos/Greenloop36/ix-ApplicationCentre_Status/contents/"
DownloadFilePath = "https://raw.githubusercontent.com/Greenloop36/ix-ApplicationCentre_Status/main/"

## init
Root = None

## Variables
RefreshDebounce = 0
CurrentRow = 0
CurrentData = {}
ContentFrame = None

## Methods
def GetStatus() -> tuple[bool, dict | str]:
    Success, Result = update.ProtectedRequest(f"{DownloadFilePath}/Status.json")

    if Success:
        try:
            Data = Result.json()
        except:
            return False, "Could not decode JSON!"
        else:
            return True, Data
    else:
        return False, str(Result)

def SetStatus(Data: dict) -> tuple[bool, str | None]:
    ## Convert dict to JSON (str)
    try:
        Data = json.dumps(Data)
    except:
        return False, "Could not dump JSON to string!"

    ## Encode with base64, as github requires that format
    try:
        Data = base64.b64encode(Data).decode("utf-8")
    except:
        return False, "Could not encode to Base64!"
    
    ## Commit
    Success, Result = update.ProtectedPost(f"{API}/Status.json", {
        "message": "Update centre from remote control",
        "content": Data
    })

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

        if Type == "str":
            Variable = StringVar(Root)
            Object = ttk.Entry(Container, textvariable=Variable)
            Root.update()
            Variable.set(Value)
        elif Type == "bool":
            Variable = BooleanVar(Root)
            Object = ttk.Checkbutton(Container, variable=Variable)
            Root.update()
            Variable.set(Value)
            print()
        elif Type == "dict":
            SaveTo[Index] = {}
            CreateObjectsForDict(Value, Container, DefaultPadding + Indent, SaveTo[Index])
            continue
        
        Object.grid(row=CurrentRow, column=2, sticky="e", pady=(0, DefaultPadding))
        

def RefreshWindow() -> bool:
    global ContentFrame, CurrentRow, RefreshDebounce

    if RefreshDebounce > time.time():
        return messagebox.showwarning("Warning", "Please wait before sending another request.")
    else:
        RefreshDebounce = time.time() + 5

    CurrentRow = 0

    ClearFrame(ContentFrame)
    Root.update()

    GetSuccess, StatusData = GetStatus()

    if not GetSuccess:
        messagebox.showerror("Error", f"Could not retrieve status information: {StatusData}")

        return
    else:
        print(GetSuccess, StatusData)

    CreateObjectsForDict(StatusData, ContentFrame)

def OnSubmit():
    pass

def main():
    global ContentFrame, Root
    ## Get status
    


    ## UI
    Root = Tk()
    Root.title(ProgramTitle)
    Root.resizable(False, False)

    HeaderFont = font.Font(size = 16, weight = "bold")

    
    # Header
    HeaderFrame = ttk.Frame(Root)
    HeaderFrame.grid(sticky="w")
    ttk.Label(HeaderFrame, text=ProgramTitle, font=HeaderFont, anchor = "w").grid(column=0, row=0, sticky="w", padx=(DefaultPadding, 30),pady=(DefaultPadding, 0))
    ttk.Label(HeaderFrame, text="Remote control interface", anchor = "w").grid(column=0, row=1, sticky="w", padx=(DefaultPadding, 30), pady=(0, DefaultPadding))

    # Content
    ContentFrame = ttk.Frame(Root, padding=10)
    ContentFrame.grid(sticky="nwse")

    RefreshWindow()

    # Buttons
    ButtonsFrame = ttk.Frame(Root, padding = 10)
    ButtonsFrame.grid(sticky="E")
    ttk.Button(ButtonsFrame, text="Refresh", command=RefreshWindow).grid(column=1, row=0, sticky="E", padx=(0, DefaultPadding))
    SubmitButton = ttk.Button(ButtonsFrame, text="Submit", command=OnSubmit)
    SubmitButton.grid(column=2, row=0, sticky="E")

    ## Run
    Root.mainloop()

## Runtime
if __name__ == "__main__":
    main()