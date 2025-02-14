"""

Utils
September 2024
upd December 2024

"""

# variables
import time
from datetime import datetime

# @class UserInput
class UserInput:
    def OptionsList(options: list, prompt: str = None) -> str:
        """
            Creates an options list, returning the string value of the selected option.
            A custom prompt is able to be specified, however this is optional.
        """
        
        # variables
        selection: any = None
        count: int = 0

        # init
        if prompt == None:
            prompt = "Select an option from below:"
        
        # runtime
        print(prompt)
        for value in options:
            print(f"    [{count + 1}]", value)
            count += 1
        
        while True:
            selection = input("> ")
            try:
                selection = int(selection)
            except:
                print(" [!] Invalid selection! (not a number)")
            else:
                try:
                    options[selection - 1]
                except:
                    print(" [!] Invalid selection! (not an option)")
                else:
                    return str(options[selection - 1])
    def YesNo(prompt: str = None) -> bool:
        print(prompt,"(Y/n)")

        while True:
            selection: str = input("> ")
            selection = selection.lower()

            if selection == "y":
                return True
            elif selection == "n":
                return False
    
    def ParseCommandInput(Query: str) -> tuple[bool, str | None, str | None]:
        try:
            Parts = Query.split(" ", 1)
            Command = Parts[0]
            Params = len(Parts) > 1 and Parts[1] or None
        except:
            return False, None, None
        else:
            return True, Command, Params

        
