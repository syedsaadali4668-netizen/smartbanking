"""
Account Model - Defines the Account class for the Smart Banking System
"""
import json
from datetime import datetime


class Account:
    """Represents a bank account with all relevant details."""

    _id_counter = 1000  # Static counter for auto-generating account IDs

    def __init__(self, name, balance=0.0, account_type="Savings", pin="1234"):
        Account._id_counter += 1
        self.id = f"ACC{Account._id_counter}"
        self.name = name
        self.balance = float(balance)
        self.account_type = account_type
        self.pin = str(pin)          # Always store as string
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions = []
        self.is_active = True
        self.risk_score = 0          # For fraud detection

    def deposit(self, amount):
        """Deposit money into the account."""
        if amount <= 0:
            return False, "Amount must be positive!"
        self.balance += amount
        return True, f"Successfully deposited ${amount:,.2f}"

    def withdraw(self, amount):
        """Withdraw money from the account."""
        if amount <= 0:
            return False, "Amount must be positive!"
        if amount > self.balance:
            return False, "Insufficient funds!"
        self.balance -= amount
        return True, f"Successfully withdrew ${amount:,.2f}"

    def to_dict(self):
        """Convert account to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "balance": self.balance,
            "account_type": self.account_type,
            "pin": str(self.pin),    # Always save as string
            "created_at": self.created_at,
            "transactions": self.transactions,
            "is_active": self.is_active,
            "risk_score": self.risk_score
        }

    @classmethod
    def from_dict(cls, data):
        """Create an Account instance from a dictionary (bypasses __init__)."""
        acc = cls.__new__(cls)
        acc.id = data["id"]
        acc.name = data["name"]
        acc.balance = float(data["balance"])
        acc.account_type = data["account_type"]
        acc.pin = str(data["pin"])   # Always load as string
        acc.created_at = data["created_at"]
        acc.transactions = data.get("transactions", [])
        acc.is_active = data.get("is_active", True)
        acc.risk_score = data.get("risk_score", 0)

        # CRITICAL: update class counter so new accounts don't collide with loaded ones
        try:
            num = int(data["id"].replace("ACC", ""))
            if num > Account._id_counter:
                Account._id_counter = num
        except (ValueError, AttributeError):
            pass

        return acc

    def __str__(self):
        return f"Account({self.id}, {self.name}, ${self.balance:,.2f})"

    def __lt__(self, other):
        return self.balance < other.balance

    def __gt__(self, other):
        return self.balance > other.balance

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)