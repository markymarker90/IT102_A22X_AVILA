# ######### Learning Signature ######### 
# Programmed by: Minard Angelo Avila
# Date Submitted: September 5, 2026
# 
# Program Description: A Python and Streamlit ATM application that uses Object-Oriented
# Programming to manage user accounts. It enables secure login, deposits, withdrawals, 
# transfers, bills payment, and transaction tracking via local text file storage.
# Reflection: I learned how to practically apply the four OOP pillars (Encapsulation, 
# Abstraction, Inheritance, Polymorphism) to structure a Python app. I also learned 
# how to secure data with protected attributes and integrate backend logic with a UI. 
# AI Usage
# [ ] No AI Assistance – Completed independently without AI.
# [x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
# [ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.

import streamlit as st
import time

import avila_bank_auth
import avila_bank_storage
import avila_bank_transactions
import avila_bank_analysis
import  avila_bank_utils

# ==========================================
# PAGE CONFIGURATION & CSS (Dark Mode)
# ==========================================
st.set_page_config(page_title="Avila Trust Bank | Online Portal", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0b1120 !important; font-family: 'Inter', sans-serif; }
    p, h1, h2, h3, h4, h5, h6, span, label, .st-emotion-cache-1wivap2 { color: #f1f5f9 !important; }
    .st-emotion-cache-1629p8f p { color: #94a3b8 !important; }
    
    .brand-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px 30px; border-radius: 12px; border: 1px solid #334155;
        margin-bottom: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    .brand-banner h1 { font-weight: 700; margin: 0; font-size: 1.85rem; display: flex; align-items: center; gap: 12px; color: #ffffff !important; }
    .brand-banner p { color: #94a3b8 !important; margin: 6px 0 0 0; font-size: 0.95rem; }

    [data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #334155 !important; background-color: #151e32 !important; border-radius: 12px !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 8px; }
    input { color: #f1f5f9 !important; }
    div[data-baseweb="input"]:focus-within > div { border-color: #38bdf8 !important; box-shadow: 0 0 0 1px #38bdf8 !important; }

    div.stButton > button { border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s ease-in-out !important; padding: 0.5rem 1rem !important; }
    div.stButton > button[kind="primary"] { background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important; color: white !important; border: none !important; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.4) !important; }
    div.stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important; transform: translateY(-1px); }
    div.stButton > button[kind="secondary"] { background-color: #1e293b !important; color: #f1f5f9 !important; border: 1px solid #475569 !important; }
    div.stButton > button[kind="secondary"]:hover { border-color: #94a3b8 !important; background-color: #334155 !important; }

    div[data-testid="stMetric"] { background-color: #1e293b !important; border: 1px solid #334155 !important; padding: 16px 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2); }
    div[data-testid="stMetric"] label { color: #94a3b8 !important; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f8fafc !important; font-weight: 700; }

    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
    [data-testid="stSidebar"] hr { border-color: #334155 !important; }
    .sidebar-profile { background-color: #1e293b; padding: 16px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 20px; }
    .sidebar-profile h3 { color: #38bdf8 !important; margin: 0; font-size: 1.1rem; }
    .sidebar-profile .badge { display: inline-block; background: #0284c7; color: #ffffff !important; font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 9999px; margin-top: 6px; text-transform: uppercase; }
    .sidebar-profile p { color: #94a3b8 !important; margin: 6px 0 0 0; font-size: 0.85rem; font-family: monospace; }
</style>
""", unsafe_allow_html=True)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "account" not in st.session_state:
    st.session_state.account = None

st.markdown("""
<div class="brand-banner">
    <h1>🏛️ AVILA TRUST BANK</h1>
    <p>Enterprise Self-Service ATM & Digital Banking Terminal</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION
# ==========================================
if not st.session_state.logged_in:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        login_tab, register_tab = st.tabs(["🔐 Authorized Login", "📝 Open Account"])
        
        with login_tab:
            with st.container(border=True):
                st.subheader("Account Login")
                st.caption("Enter your credentials to access your ATM session.")
                account_number = st.text_input("Account Number", placeholder="e.g. 1001", key="login_account")
                pin = st.text_input("PIN", type="password", max_chars=4, placeholder="••••", key="login_pin")
                st.write("")
                if st.button("Authenticate Session ➔", use_container_width=True, type="primary"):
                    account, message = avila_bank_auth.login_account(account_number, pin)
                    if account is not None:
                        st.session_state.logged_in = True
                        st.session_state.account = account
                        st.rerun()
                    else:
                        st.error(message)

        with register_tab:
            with st.container(border=True):
                st.subheader("New Account Registration")
                st.caption("Register a new checking/savings profile.")
                name = st.text_input("Account Holder Full Name", key="register_name")
                account_number = st.text_input("Desired Account Number", key="register_account")
                c1, c2 = st.columns(2)
                with c1: pin = st.text_input("4-Digit PIN", type="password", max_chars=4, key="register_pin")
                with c2: confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4, key="register_confirm_pin")
                c3, c4 = st.columns(2)
                with c3: account_type = st.selectbox("Account Tier", ["Savings Account", "Student Account"])
                with c4: starting_balance = st.number_input("Initial Deposit (PHP)", min_value=0.0, step=100.0, format="%.2f")
                st.write("")
                if st.button("Complete Registration", use_container_width=True, type="secondary"):
                    account, message = avila_bank_auth.register_account(name, account_number, pin, confirm_pin, account_type, starting_balance)
                    if account is not None:
                        st.success(f"{message} Please proceed to the Login tab.")
                    else:
                        st.error(message)

# ==========================================
# AUTHENTICATED ATM PORTAL
# ==========================================
else:
    account = st.session_state.account

    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-profile">
            <h3>{account.account_name}</h3>
            <span class="badge">{account.get_account_type()}</span>
            <p>ACCT: #{account.account_number}</p>
        </div>
        """, unsafe_allow_html=True)

        menu = st.radio(
            "TERMINAL MENU",
            [
                "📊 Dashboard",
                "💵 Deposit Funds",
                "💳 Withdraw Cash",
                "💸 Fund Transfer",       # NEW
                "🧾 Pay Bills",           # NEW
                "📱 Mobile Load",         # NEW
                "📄 Statement & History",
                "📈 Financial Analytics",
                "⚙️ Account Settings"     # NEW
            ]
        )
        st.divider()
        if st.button("🔒 Terminate Session", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.account = None
            st.rerun()

    # 1. DASHBOARD
    if menu == "📊 Dashboard":
        st.subheader("Account Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Available Balance", avila_bank_utils.format_currency(account.check_balance()))
        col2.metric("Account Tier", account.get_account_type())
        col3.metric("Account ID", f"#{account.account_number}")

    # 2. DEPOSIT
    elif menu == "💵 Deposit Funds":
        st.subheader("Deposit Currency")
        with st.container(border=True):
            st.markdown(f"**Current Balance:** `{avila_bank_utils.format_currency(account.check_balance())}`")
            amount = st.number_input("Deposit Amount (PHP)", min_value=0.0, step=100.0, format="%.2f")
            if st.button("Confirm Deposit", type="primary", use_container_width=True):
                if avila_bank_utils.is_valid_amount(amount):
                    if account.deposit(amount):
                        avila_bank_storage.update_account(account)
                        avila_bank_transactions.record_transaction(account, "Deposit", amount)
                        st.success("Funds successfully credited.")
                        st.rerun()
                else:
                    st.error("Invalid amount.")

    # 3. WITHDRAW
    elif menu == "💳 Withdraw Cash":
        st.subheader("Withdraw Currency")
        with st.container(border=True):
            st.markdown(f"**Available Balance:** `{avila_bank_utils.format_currency(account.check_balance())}`")
            amount = st.number_input("Withdrawal Amount (PHP)", min_value=0.0, step=100.0, format="%.2f")
            if st.button("Dispense Cash", type="primary", use_container_width=True):
                if not avila_bank_utils.is_valid_amount(amount):
                    st.error("Invalid amount.")
                elif amount > account.check_balance():
                    st.error("Insufficient funds.")
                else:
                    try:
                        if account.withdraw(amount):
                            avila_bank_storage.update_account(account)
                            avila_bank_transactions.record_transaction(account, "Withdraw", amount)
                            st.success("Cash dispensed successfully.")
                            st.rerun()
                    except ValueError as e:
                        st.error(str(e)) # Catches student limits if implemented

    # 4. NEW FEATURE: FUND TRANSFER
    elif menu == "💸 Fund Transfer":
        st.subheader("P2P Money Transfer")
        with st.container(border=True):
            st.caption("Send funds instantly to another Avila Trust Bank account.")
            st.markdown(f"**Available Balance:** `{avila_bank_utils.format_currency(account.check_balance())}`")
            
            target_acct = st.text_input("Recipient Account Number", placeholder="Enter exact Account ID")
            amount = st.number_input("Transfer Amount (PHP)", min_value=0.0, step=100.0, format="%.2f")
            
            if st.button("Send Funds ➔", type="primary", use_container_width=True):
                if target_acct == account.account_number:
                    st.error("You cannot transfer funds to your own account.")
                elif not avila_bank_utils.is_valid_amount(amount):
                    st.error("Please enter a valid amount.")
                elif amount > account.check_balance():
                    st.error("Insufficient balance for this transfer.")
                else:
                    recipient = avila_bank_storage.find_account(target_acct)
                    if recipient is None:
                        st.error("Recipient account not found in the database.")
                    else:
                        # OOP Interaction: Withdraw from self, Deposit to recipient
                        account.withdraw(amount)
                        recipient.deposit(amount)
                        # Save both
                        avila_bank_storage.update_account(account)
                        avila_bank_storage.update_account(recipient)
                        # Log transactions
                        avila_bank_transactions.record_transaction(account, f"Transfer to #{target_acct}", amount)
                        avila_bank_transactions.record_transaction(recipient, f"Transfer from #{account.account_number}", amount)
                        
                        st.success(f"Successfully transferred {avila_bank_utils.format_currency(amount)} to {recipient.account_name}!")
                        time.sleep(1)
                        st.rerun()

    # 5. NEW FEATURE: BILLS PAYMENT
    elif menu == "🧾 Pay Bills":
        st.subheader("Utilities & Biller Payment")
        with st.container(border=True):
            biller = st.selectbox("Select Registered Biller", ["Meralco (Electricity)", "Maynilad (Water)", "PLDT (Internet)", "Globe Postpaid"])
            subscriber_no = st.text_input("Subscriber Account Number", max_chars=12)
            amount = st.number_input("Payment Amount (PHP)", min_value=0.0, step=50.0, format="%.2f")
            
            if st.button("Process Payment", type="primary", use_container_width=True):
                if not subscriber_no.isdigit():
                    st.error("Subscriber number must contain only numbers.")
                elif not avila_bank_utils.is_valid_amount(amount):
                    st.error("Invalid payment amount.")
                elif amount > account.check_balance():
                    st.error("Insufficient funds.")
                else:
                    if account.withdraw(amount):
                        avila_bank_storage.update_account(account)
                        # Log as a specific transaction type
                        avila_bank_transactions.record_transaction(account, f"Bills Payment: {biller}", amount)
                        st.success(f"Payment of {avila_bank_utils.format_currency(amount)} to {biller} was successful!")
                        time.sleep(1)
                        st.rerun()

    # 6. NEW FEATURE: MOBILE LOAD
    elif menu == "📱 Mobile Load":
        st.subheader("Buy Prepaid Load & Promos")
        with st.container(border=True):
            network = st.radio("Select Network", ["Globe", "Smart", "DITO", "TNT"], horizontal=True)
            mobile_no = st.text_input("11-Digit Mobile Number", placeholder="09xxxxxxxxx", max_chars=11)
            
            load_type = st.selectbox("Select Load Package", [
                "Regular Load - ₱50.00", 
                "Regular Load - ₱100.00", 
                "Promo: Surf & Text - ₱99.00",
                "Promo: Unli All Net - ₱149.00"
            ])
            
            # Extract price from string using string manipulation
            price_str = load_type.split("₱")[1]
            amount = float(price_str)
            
            if st.button("Purchase Load", type="primary", use_container_width=True):
                if len(mobile_no) != 11 or not mobile_no.startswith("09"):
                    st.error("Please enter a valid 11-digit mobile number starting with 09.")
                elif amount > account.check_balance():
                    st.error("Insufficient funds.")
                else:
                    if account.withdraw(amount):
                        avila_bank_storage.update_account(account)
                        avila_bank_transactions.record_transaction(account, f"E-Load ({network}): {mobile_no}", amount)
                        st.success(f"{load_type} successfully sent to {mobile_no}.")
                        time.sleep(1)
                        st.rerun()

    # 7. STATEMENT & HISTORY
    elif menu == "📄 Statement & History":
        st.subheader("Account Statement Ledger")
        transactions = avila_bank_transactions.get_transactions()
        user_transactions = [t for t in transactions if t.get("account_number") == account.account_number]
        if user_transactions:
            display_data = []
            for t in reversed(user_transactions):
                display_data.append({
                    "Timestamp": t.get("timestamp", "N/A"),
                    "Type": t.get("transaction", "N/A"),
                    "Amount": avila_bank_utils.format_currency(t.get("amount", 0)),
                    "Balance Ledger": avila_bank_utils.format_currency(t.get("balance_after", 0))
                })
            st.dataframe(display_data, use_container_width=True, hide_index=True)
        else:
            st.info("No prior transaction events registered.")

    # 8. FINANCIAL ANALYTICS
    elif menu == "📈 Financial Analytics":
        st.subheader("Financial Performance")
        result = avila_bank_analysis.analyze_transactions(account.account_number)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Events", result["total_transactions"])
        c2.metric("Deposits Logged", result["deposits"])
        c3.metric("Withdrawals Logged", result["withdrawals"])

    # 9. NEW FEATURE: ACCOUNT SETTINGS
    elif menu == "⚙️ Account Settings":
        st.subheader("Security Settings")
        with st.container(border=True):
            st.markdown("#### Change ATM PIN")
            st.caption("Update your 4-digit security PIN. Never share this with anyone.")
            
            current_pin = st.text_input("Current PIN", type="password", max_chars=4)
            c1, c2 = st.columns(2)
            with c1:
                new_pin = st.text_input("New 4-Digit PIN", type="password", max_chars=4)
            with c2:
                confirm_new_pin = st.text_input("Confirm New PIN", type="password", max_chars=4)
                
            if st.button("Update Security PIN", type="primary"):
                if new_pin != confirm_new_pin:
                    st.error("New PINs do not match.")
                else:
                    # Attempt to update via the newly encapsulated method
                    try:
                        success, msg = account.change_pin(current_pin, new_pin)
                        if success:
                            avila_bank_storage.update_account(account) # Saves the object to the file
                            st.success(msg)
                        else:
                            st.error(msg)
                    except AttributeError:
                        st.error("Error: Please ensure the change_pin() method was added to avila_bank_account.py.")