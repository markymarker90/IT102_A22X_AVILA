# TODO 1:
# Create a function named check_balance().
# The function should receive an Account object.
def check_balance(account):

    # TODO 2:
    # Ask the Account object for its
    # current balance.
    # Return the result to the caller.
    return account.check_balance()
""" 
######### Learning Signature ######### 
Programmed by: Minard Angelo Avila
Date Submitted: September 4, 2026
 
Program Description: This program defines a bridge module that receives an Account object as a parameter and retrieves its current balance for the frontend.
Reflection: I learned how to pass objects 
into functions and return their internal values, 
which cleanly decouples the core object-oriented data from the Streamlit user interface so the balance can be safely displayed as a web metric.
 
AI Usage
[ ] No AI Assistance – Completed independently without AI.
[x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
[ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.
"""