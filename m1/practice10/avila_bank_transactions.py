from datetime import datetime


TRANSACTIONS_FILE = "transactions.txt"


def record_transaction(account, transaction_type, amount):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(TRANSACTIONS_FILE, "a") as file:
        file.write(f"Timestamp: {timestamp}\n")
        file.write(f"Account Number: {account.account_number}\n")
        file.write(f"Account: {account.account_name}\n")
        file.write(f"Account Type: {account.get_account_type()}\n")
        file.write(f"Transaction: {transaction_type}\n")
        file.write(f"Amount: ₱{amount:.2f}\n")
        file.write(f"Balance After: ₱{account.check_balance():.2f}\n\n")


def get_transactions():
    transactions = []

    try:
        with open(TRANSACTIONS_FILE, "r") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return transactions

    current = {}

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("Timestamp:"):
            current["timestamp"] = line.replace("Timestamp:", "").strip()

        elif line.startswith("Account Number:"):
            current["account_number"] = line.replace("Account Number:", "").strip()

        elif line.startswith("Account:"):
            current["account"] = line.replace("Account:", "").strip()

        elif line.startswith("Account Type:"):
            current["account_type"] = line.replace("Account Type:", "").strip()

        elif line.startswith("Transaction:"):
            current["transaction"] = line.replace("Transaction:", "").strip()

        elif line.startswith("Amount:"):
            amount_text = line.replace("Amount: ₱", "").replace(",", "").strip()
            try:
                current["amount"] = float(amount_text)
            except ValueError:
                current["amount"] = 0.0

        elif line.startswith("Balance After:"):
            balance_text = line.replace("Balance After: ₱", "").replace(",", "").strip()
            try:
                current["balance_after"] = float(balance_text)
            except ValueError:
                current["balance_after"] = 0.0

            if (
                "timestamp" in current
                and "account_number" in current
                and "transaction" in current
                and "amount" in current
            ):
                transactions.append(current.copy())

            current = {}

    return transactions