from abc import ABC, abstractmethod

# ABSTRACTION: Inheriting from ABC (Abstract Base Class) prevents BankAccount 
# from being instantiated directly. It acts purely as a blueprint.
class BankAccount(ABC):
    def __init__(self, account_number, name, pin, starting_balance):
        self.account_number = account_number
        self.account_name = name
        
        # ENCAPSULATION: The single underscore denotes these attributes are protected.
        # They should not be manipulated directly from outside the class.
        self._pin = pin
        self._balance = starting_balance

    def check_balance(self):
        return self._balance

    # ENCAPSULATION (IMPROVEMENT): A setter method provides a secure, controlled 
    # way to update the balance without directly exposing the _balance attribute.
    def set_balance(self, amount):
        if amount >= 0:
            self._balance = amount

    def deposit(self, amount):
        # IMPROVEMENT: Raising specific ValueErrors instead of returning False 
        # makes debugging easier and prevents silent failures.
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self._balance += amount
        return True

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self._balance:
            raise ValueError("Insufficient balance.")
        self._balance -= amount
        return True

    def verify_pin(self, pin):
        return self._pin == pin

    def get_pin(self):
        return self._pin
# Add this inside the BankAccount class, right below verify_pin()
    def change_pin(self, current_pin, new_pin):
        """Encapsulated method to safely update the account's PIN."""
        if not self.verify_pin(current_pin):
            return False, "Current PIN is incorrect."
        if not new_pin.isdigit() or len(new_pin) != 4:
            return False, "New PIN must be exactly 4 digits."
        
        self._pin = new_pin
        return True, "PIN successfully updated."
    # ABSTRACTION: The @abstractmethod decorator forces any child class 
    # that inherits BankAccount to provide its own version of this method.
    @abstractmethod
    def get_account_type(self):
        pass

# INHERITANCE: SavingsAccount automatically inherits all attributes and 
# core methods (like deposit and withdraw) from the BankAccount base class.
class SavingsAccount(BankAccount):
    
    # POLYMORPHISM: The child class implements its own specific version 
    # of the abstract method defined in the parent class.
    def get_account_type(self):
        return "Savings Account"

# INHERITANCE: StudentAccount also inherits from the BankAccount base class.
class StudentAccount(BankAccount):
    
    # POLYMORPHISM: Provides a different return value than SavingsAccount.
    def get_account_type(self):
        return "Student Account"
        
    # POLYMORPHISM (IMPROVEMENT): Overriding the parent's withdraw() method 
    # allows us to implement distinct business rules (a withdrawal limit) 
    # specifically for students, while still utilizing the parent's logic via super().
    def withdraw(self, amount):
        if amount > 5000:
            raise ValueError("Student accounts have a ₱5,000 withdrawal limit.")
        return super().withdraw(amount)
    """ 
######### Learning Signature ######### 
Programmed by: Minard Angelo Avila
Date Submitted: September 5, 2026
 
Program Description: A Python and Streamlit ATM application that uses Object-Oriented
 Programming to manage user accounts. It enables secure login, deposits,
 withdrawals, and transaction tracking via local text file storage.
Reflection: I learned how to practically apply the four OOP pillars (Encapsulation, Abstraction, Inheritance, Polymorphism)
 to structure a Python app. I also learned how to secure data with protected attributes and integrate backend logic with a Streamlit frontend. 
AI Usage
[ ] No AI Assistance – Completed independently without AI.
[x] AI as Support Tool – Used AI for explanations, syntax, or minor corrections.
[ ] AI as Collaborative Partner – Used AI to design, structure, or co-create significant code.
"""