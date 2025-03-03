from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from . import update
import json
import base64
import time

## Configuration
DefaultPadding = 10
ProgramTitle = "Application Centre Controller"
API = "https://api.github.com/repos/Greenloop36/ix-ApplicationCentre_Status/contents"
DownloadFilePath = "https://raw.githubusercontent.com/Greenloop36/ix-ApplicationCentre_Status/main/"

## init
Root = None

## Variables
Token = None
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
        Data: str = json.dumps(Data)
    except Exception as e:
        print(f"[SetStatus]: dumps failed: {e}")
        return False, "Could not dump JSON to string!"

    ## Encode with base64, as github requires that format
    try:
        Data = base64.b64encode(Data.encode("utf-8"))
    except Exception as e:
        print(f"[SetStatus]: b64encode failed: {e}")
        return False, "Could not encode to Base64!"
    
    ## Commit
    print(Token)
    return update.CustomRequest(f"{API}/Status.json", "PUT", {
        "message": "Update centre from remote control",
        "content": Data
    }, {"Authorisation": Token})

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

    CurrentData = CreateObjectsForDict(StatusData, ContentFrame)

def OnSubmit():
    Target = TkObjectsToDict(CurrentData)
    Success, Result = SetStatus(Target)
    RefreshWindow(True)

    if Success:
        return messagebox.showinfo(ProgramTitle, "Successfully updated centre status.")
    else:
        return messagebox.showerror(ProgramTitle, f"Failed to commit: {Result}")

def main():
    global ContentFrame, Root, Token
    ## Get status

    ## UI
    Root = Tk()
    Root.title(ProgramTitle)
    Root.resizable(False, False)
    Token = update.GetToken()
    Root.option_add('*tearOff', FALSE)

    ## Menubar
    # Menubar = Menu(Root)
    # Root["menu"] = Menubar
    # Menu_Edit = Menu(Menubar)

    # Menubar.add_cascade(menu=Menu_Edit, label="Edit")
    # Menu_Edit.add_command(label="Edit Token", command=TokenWindow)


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
    main()