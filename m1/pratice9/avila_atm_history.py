# TODO 1:
# Create view_history().
def view_history():
    # TODO 2:
    # Try to open transactions.txt
    # in read mode.
    try:
        with open("transactions.txt", "r", encoding="utf-8") as file:
            # TODO 3:
            # Read all lines from the file.
            lines = file.readlines()
            
            # TODO 4:
            # Return the lines to the caller.
            return lines
            
    # TODO 5:
    # Handle FileNotFoundError.
    #
    # If the file does not exist,
    # return an empty list.
    except FileNotFoundError:
        return []
""" 
######### Learning Signature ######### 
Programmed by: Minard Angelo Avila
Date Submitted: September 4, 2026
 
Program Description: This program reads and retrieves logged transaction records from a text file to display account history.
Reflection: I learned how to handle file input/output operations safely and manage missing files using exception handling.
 
AI Usage
[ ] No AI Assistance – Completed independently without AI.
[x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
[ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.
"""