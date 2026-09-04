from datetime import datetime

def deposit_money(account, amount):
    if amount <= 0:
        return False

    success = account.deposit(amount)

    if success:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("transactions.txt", "a", encoding="utf-8") as file:
            file.write(f"Timestamp: {timestamp}\n")
            file.write(f"Account: {account.account_name}\n")
            file.write("Transaction: Deposit\n")
            file.write(f"Amount: ₱{amount:.2f}\n\n")
        return True

    return False
""" 
######### Learning Signature ######### 
Programmed by: Minard Angelo Avila
Date Submitted: September 4, 2026
 
Program Description: his program defines the deposit module that validates transaction
 amounts, calls the Account object to update the balance, and appends a formatted timestamp record to transactions.txt
Reflection: I learned how to integrate file processing with object-oriented methods to persist transactional data securely and log activities with timestamps.
AI Usage
[ ] No AI Assistance – Completed independently without AI.
[x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
[ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.
"""