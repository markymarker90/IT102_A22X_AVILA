import os

def analyze_transactions():
    # TODO 1:
    # Try to open transactions.txt.
    #
    # Read all lines from the file.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "transactions.txt")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
    # TODO 2:
    # If the file does not exist,
    # return a dictionary containing
    # zero or "None" values for the
    # required analysis results.
    except FileNotFoundError:
        return {
            "total_transactions": 0,
            "deposits": 0,
            "withdrawals": 0,
            "total_deposited": 0.0,
            "total_withdrawn": 0.0,
            "average_transaction": 0.0,
            "largest_transaction": 0.0,
            "latest_transaction": "None",
            "latest_timestamp": "None"
        }
 
    # TODO 3:
    # Create an empty list named transactions.
    transactions = []
 
    # TODO 4:
    # Create an empty dictionary named current.
    #
    # This dictionary will temporarily
    # store one transaction.
    current = {}
 
    # TODO 5:
    # Use a for loop to process every line.
    for line in lines:
        # TODO 6:
        # Remove unnecessary spaces and
        # newline characters.
        line = line.strip()
 
        # TODO 7:
        # Ignore empty lines.
        if not line:
            if current:
                # TODO 12:
                # Once the required transaction
                # information has been collected,
                # add the transaction to the
                # transactions list.
                transactions.append(current)
                current = {}
            continue
 
        # TODO 8:
        # Detect lines beginning with:
        #
        # Timestamp:
        #
        # Store the timestamp.
        if line.startswith("Timestamp:"):
            current["timestamp"] = line.split(":", 1)[1].strip()
 
        # TODO 9:
        # Detect lines beginning with:
        #
        # Account:
        #
        # Store the account name.
        elif line.startswith("Account:"):
            current["account"] = line.split(":", 1)[1].strip()
 
        # TODO 10:
        # Detect lines beginning with:
        #
        # Transaction:
        #
        # Store the transaction type.
        elif line.startswith("Transaction:"):
            current["type"] = line.split(":", 1)[1].strip()
 
        # TODO 11:
        # Detect lines beginning with:
        #
        # Amount:
        #
        # Convert the amount to a float.
        elif line.startswith("Amount:"):
            amount_str = line.split(":", 1)[1].replace("₱", "").replace(",", "").strip()
            try:
                current["amount"] = float(amount_str)
            except ValueError:
                current["amount"] = 0.0

    # Catch the last record block if file doesn't end with a blank line
    if current:
        transactions.append(current)
 
    # TODO 13:
    # Calculate the total number
    # of transactions.
    total_transactions = len(transactions)
 
    # TODO 14:
    # Count the number of deposits.
    deposits = 0
 
    # TODO 15:
    # Count the number of withdrawals.
    withdrawals = 0
 
    # TODO 16:
    # Calculate the total amount
    # deposited.
    total_deposited = 0.0
 
    # TODO 17:
    # Calculate the total amount
    # withdrawn.
    total_withdrawn = 0.0
 
    # TODO 18:
    # Determine the largest transaction.
    largest_transaction = 0.0

    for t in transactions:
        t_type = t.get("type", "")
        t_amount = t.get("amount", 0.0)

        if t_amount > largest_transaction:
            largest_transaction = t_amount

        if t_type == "Deposit":
            deposits += 1
            total_deposited += t_amount
        elif t_type == "Withdraw":
            withdrawals += 1
            total_withdrawn += t_amount
 
    # TODO 19:
    # Determine the latest transaction type.
    latest_transaction = transactions[-1].get("type", "None") if transactions else "None"
 
    # TODO 20:
    # Determine the latest timestamp.
    latest_timestamp = transactions[-1].get("timestamp", "None") if transactions else "None"
 
    # TODO 21:
    # Calculate the average transaction amount.
    #
    # Avoid division by zero.
    total_sum = total_deposited + total_withdrawn
    average_transaction = (total_sum / total_transactions) if total_transactions > 0 else 0.0
 
    # TODO 22:
    # Return all calculated results
    # inside one dictionary.
    return {
        "total_transactions": total_transactions,
        "deposits": deposits,
        "withdrawals": withdrawals,
        "total_deposited": total_deposited,
        "total_withdrawn": total_withdrawn,
        "average_transaction": average_transaction,
        "largest_transaction": largest_transaction,
        "latest_transaction": latest_transaction,
        "latest_timestamp": latest_timestamp
    }

""" 
######### Learning Signature ######### 
Programmed by: Minard Angelo Avila
Date Submitted: September 4, 2026
 
Program Description: This program parses transaction records from a text file to calculate and summarize financial metrics such as total transactions, deposits, withdrawals, and averages.
Reflection: I learned how to read, split, and process structured line items from text files to aggregate data into a summary dictionary.
 
AI Usage
[ ] No AI Assistance – Completed independently without AI.
[x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
[ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.
"""