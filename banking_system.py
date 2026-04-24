"""
Banking System Service - Core logic connecting all components
"""
import json
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.account import Account
from models.transaction import Transaction
from data_structures.linked_list import LinkedList
from data_structures.stack import Stack
from data_structures.queue import Queue
from data_structures.bst import BinarySearchTree
from data_structures.hash_table import HashTable
from utils.search import linear_search, binary_search, search_by_name
from utils.sorting import sort_accounts_by_balance, sort_accounts_by_name
from services.fraud_detection import FraudDetector


class BankingSystem:
    """
    Core Banking System - The brain of the application.
    Connects all data structures and services.
    """

    def __init__(self):
        # Data structures
        self.accounts_hash = HashTable(capacity=101)       # Fast lookup by ID
        self.accounts_bst = BinarySearchTree()             # Sorted by balance
        self.customer_list = LinkedList()                  # Customer records
        self.transaction_queue = Queue()                   # Pending transactions
        self.undo_stack = Stack(max_size=50)               # Undo history
        self.fraud_detector = FraudDetector()              # Fraud detection

        # Admin credentials
        self.admin_username = "admin"
        self.admin_password = "admin123"

        # Data file paths
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.accounts_file = os.path.join(self.data_dir, "accounts.json")
        self.transactions_file = os.path.join(self.data_dir, "transactions.json")

        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)

        # Load existing data
        self.load_data()

    # ==================== ACCOUNT MANAGEMENT ====================

    def create_account(self, name, initial_balance=0.0, account_type="Savings", pin="1234"):
        """Create a new bank account."""
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters!", None

        if initial_balance < 0:
            return False, "Initial balance cannot be negative!", None

        account = Account(name.strip(), initial_balance, account_type, pin)

        # Store in hash table (O(1) lookup)
        self.accounts_hash.put(account.id, account)

        # Store in BST (sorted by balance)
        self.accounts_bst.insert(account)

        # Add to linked list
        self.customer_list.append(account)

        # Save to file
        self.save_data()

        return True, f"Account created successfully! ID: {account.id}", account

    def get_account(self, account_id):
        """Get account by ID using hash table (O(1))."""
        return self.accounts_hash.get(account_id)

    def get_all_accounts(self):
        """Get all accounts."""
        return self.accounts_hash.values()

    def get_account_count(self):
        """Get total number of accounts."""
        return len(self.accounts_hash)

    def get_total_balance(self):
        """Get sum of all account balances."""
        return sum(acc.balance for acc in self.accounts_hash.values())

    # ==================== TRANSACTIONS ====================

    def deposit(self, account_id, amount, description=""):
        """Deposit money into account."""
        account = self.get_account(account_id)
        if not account:
            return False, "Account not found!", None

        if not account.is_active:
            return False, "Account is inactive!", None

        # Fraud detection
        is_suspicious, risk_score, alerts = self.fraud_detector.analyze_transaction(
            account, amount, "Deposit"
        )

        if is_suspicious:
            # Queue for manual review
            txn = Transaction(account_id, "Deposit", amount, description, "Pending Review")
            txn.fraud_flag = True
            self.transaction_queue.enqueue(txn)
            self.save_data()
            return False, f"Transaction flagged for review! Risk Score: {risk_score}", alerts

        # Process deposit
        success, msg = account.deposit(amount)
        if success:
            txn = Transaction(account_id, "Deposit", amount, description)
            account.transactions.append(txn.to_dict())

            # Push to undo stack
            self.undo_stack.push({
                "action": "deposit",
                "account_id": account_id,
                "amount": amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Rebuild BST (balance changed)
            self._rebuild_bst()
            self.save_data()

        return success, msg, txn

    def withdraw(self, account_id, amount, pin, description=""):
        """Withdraw money from account."""
        account = self.get_account(account_id)
        if not account:
            return False, "Account not found!", None

        if account.pin != pin:
            return False, "Incorrect PIN!", None

        if not account.is_active:
            return False, "Account is inactive!", None

        # Fraud detection
        is_suspicious, risk_score, alerts = self.fraud_detector.analyze_transaction(
            account, amount, "Withdraw"
        )

        if is_suspicious:
            txn = Transaction(account_id, "Withdraw", amount, description, "Pending Review")
            txn.fraud_flag = True
            self.transaction_queue.enqueue(txn)
            self.save_data()
            return False, f"Transaction flagged for review! Risk Score: {risk_score}", alerts

        # Process withdrawal
        success, msg = account.withdraw(amount)
        if success:
            txn = Transaction(account_id, "Withdraw", amount, description)
            account.transactions.append(txn.to_dict())

            # Push to undo stack
            self.undo_stack.push({
                "action": "withdraw",
                "account_id": account_id,
                "amount": amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Rebuild BST
            self._rebuild_bst()
            self.save_data()

        return success, msg, txn

    def transfer(self, from_id, to_id, amount, pin, description=""):
        """Transfer money between accounts."""
        from_acc = self.get_account(from_id)
        to_acc = self.get_account(to_id)

        if not from_acc or not to_acc:
            return False, "One or both accounts not found!", None

        if from_acc.pin != pin:
            return False, "Incorrect PIN!", None

        if from_id == to_id:
            return False, "Cannot transfer to the same account!", None

        # Withdraw from source
        success, msg = from_acc.withdraw(amount)
        if not success:
            return False, msg, None

        # Deposit to destination
        to_acc.deposit(amount)

        # Record transactions
        txn_from = Transaction(from_id, "Transfer Out", amount, f"To {to_id}: {description}")
        txn_to = Transaction(to_id, "Transfer In", amount, f"From {from_id}: {description}")

        from_acc.transactions.append(txn_from.to_dict())
        to_acc.transactions.append(txn_to.to_dict())

        # Push to undo stack
        self.undo_stack.push({
            "action": "transfer",
            "from_id": from_id,
            "to_id": to_id,
            "amount": amount,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Rebuild BST
        self._rebuild_bst()
        self.save_data()

        return True, f"Successfully transferred ${amount:,.2f} to {to_id}", (txn_from, txn_to)

    # ==================== SEARCH ====================

    def search_account_by_id(self, account_id):
        """Search by account ID using hash table."""
        return self.get_account(account_id)

    def search_account_by_name(self, name):
        """Search by name using linear search."""
        accounts = self.get_all_accounts()
        result, _ = search_by_name(accounts, name.lower())
        return result

    def search_accounts_by_balance_range(self, min_bal, max_bal):
        """Search accounts within balance range."""
        accounts = self.get_all_accounts()
        return [acc for acc in accounts if min_bal <= acc.balance <= max_bal]

    # ==================== SORTING ====================

    def get_sorted_by_balance(self, reverse=False):
        """Get accounts sorted by balance."""
        accounts = self.get_all_accounts()
        return sort_accounts_by_balance(accounts, reverse)

    def get_sorted_by_name(self, reverse=False):
        """Get accounts sorted by name."""
        accounts = self.get_all_accounts()
        return sort_accounts_by_name(accounts, reverse)

    # ==================== UNDO SYSTEM ====================

    def undo_last_transaction(self):
        """Undo the last transaction using stack."""
        if self.undo_stack.is_empty():
            return False, "No transactions to undo!", None

        last_action = self.undo_stack.pop()
        action = last_action["action"]
        account_id = last_action.get("account_id") or last_action.get("from_id")
        amount = last_action["amount"]

        account = self.get_account(account_id)
        if not account:
            return False, "Account no longer exists!", None

        if action == "deposit":
            account.withdraw(amount)
            msg = f"Undid deposit of ${amount:,.2f}"
        elif action == "withdraw":
            account.deposit(amount)
            msg = f"Undid withdrawal of ${amount:,.2f}"
        elif action == "transfer":
            to_id = last_action["to_id"]
            to_acc = self.get_account(to_id)
            if to_acc:
                to_acc.withdraw(amount)
                account.deposit(amount)
                msg = f"Undid transfer of ${amount:,.2f}"
            else:
                return False, "Destination account no longer exists!", None
        else:
            return False, "Unknown action type!", None

        # Rebuild BST
        self._rebuild_bst()
        self.save_data()

        return True, msg, last_action

    def get_undo_history(self):
        """Get undo history from stack."""
        return self.undo_stack.to_list()

    # ==================== ADMIN FUNCTIONS ====================

    def verify_admin(self, username, password):
        """Verify admin credentials."""
        return username == self.admin_username and password == self.admin_password

    def delete_account(self, account_id):
        """Delete an account."""
        account = self.get_account(account_id)
        if not account:
            return False, "Account not found!"

        # Remove from hash table
        self.accounts_hash.remove(account_id)

        # Remove from linked list
        self.customer_list.delete(account)

        # Rebuild BST
        self._rebuild_bst()

        self.save_data()
        return True, f"Account {account_id} deleted successfully!"

    def toggle_account_status(self, account_id):
        """Toggle account active/inactive status."""
        account = self.get_account(account_id)
        if not account:
            return False, "Account not found!"

        account.is_active = not account.is_active
        self.save_data()
        status = "activated" if account.is_active else "deactivated"
        return True, f"Account {account_id} {status}!"

    def get_system_stats(self):
        """Get comprehensive system statistics."""
        accounts = self.get_all_accounts()
        total_balance = sum(acc.balance for acc in accounts)
        avg_balance = total_balance / len(accounts) if accounts else 0

        return {
            "total_accounts": len(accounts),
            "total_balance": total_balance,
            "average_balance": avg_balance,
            "active_accounts": sum(1 for acc in accounts if acc.is_active),
            "inactive_accounts": sum(1 for acc in accounts if not acc.is_active),
            "savings_accounts": sum(1 for acc in accounts if acc.account_type == "Savings"),
            "checking_accounts": sum(1 for acc in accounts if acc.account_type == "Checking"),
            "suspicious_accounts": len(self.fraud_detector.get_suspicious_accounts()),
            "pending_transactions": len(self.transaction_queue),
            "undo_history_size": len(self.undo_stack),
            "hash_table_stats": self.accounts_hash.get_stats(),
            "bst_height": self.accounts_bst.get_height()
        }

    def get_pending_transactions(self):
        """Get all pending transactions from queue."""
        return self.transaction_queue.to_list()

    def approve_transaction(self, txn_id):
        """Approve a pending transaction."""
        # Find and remove from queue
        items = self.transaction_queue.to_list()
        for i, txn in enumerate(items):
            if txn.transaction_id == txn_id:
                # Remove from queue (rebuild without this item)
                self.transaction_queue.clear()
                for j, t in enumerate(items):
                    if j != i:
                        self.transaction_queue.enqueue(t)

                # Process the transaction
                account = self.get_account(txn.account_id)
                if account and txn.transaction_type == "Deposit":
                    account.deposit(txn.amount)
                elif account and txn.transaction_type == "Withdraw":
                    account.withdraw(txn.amount)

                self.save_data()
                return True, f"Transaction {txn_id} approved!"

        return False, "Transaction not found!"

    def reject_transaction(self, txn_id):
        """Reject a pending transaction."""
        items = self.transaction_queue.to_list()
        for i, txn in enumerate(items):
            if txn.transaction_id == txn_id:
                self.transaction_queue.clear()
                for j, t in enumerate(items):
                    if j != i:
                        self.transaction_queue.enqueue(t)
                self.save_data()
                return True, f"Transaction {txn_id} rejected!"
        return False, "Transaction not found!"

    # ==================== DATA PERSISTENCE ====================

    def _rebuild_bst(self):
        """Rebuild BST from current accounts."""
        self.accounts_bst = BinarySearchTree()
        for account in self.accounts_hash.values():
            self.accounts_bst.insert(account)

    def save_data(self):
        """Save all data to JSON files."""
        try:
            # Save accounts
            accounts_data = [acc.to_dict() for acc in self.accounts_hash.values()]
            with open(self.accounts_file, "w") as f:
                json.dump(accounts_data, f, indent=2)

            # Save transactions
            transactions_data = []
            for account in self.accounts_hash.values():
                transactions_data.extend(account.transactions)

            # Add queued transactions
            for txn in self.transaction_queue.to_list():
                transactions_data.append(txn.to_dict())

            with open(self.transactions_file, "w") as f:
                json.dump(transactions_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def load_data(self):
        """Load data from JSON files."""
        try:
            # Load accounts
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, "r") as f:
                    accounts_data = json.load(f)

                for acc_data in accounts_data:
                    account = Account.from_dict(acc_data)
                    self.accounts_hash.put(account.id, account)
                    self.accounts_bst.insert(account)
                    self.customer_list.append(account)

            # Load transactions (optional - for audit trail)
            if os.path.exists(self.transactions_file):
                with open(self.transactions_file, "r") as f:
                    _ = json.load(f)

            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def reset_system(self):
        """Reset all data (admin only)."""
        self.accounts_hash = HashTable(capacity=101)
        self.accounts_bst = BinarySearchTree()
        self.customer_list = LinkedList()
        self.transaction_queue = Queue()
        self.undo_stack = Stack(max_size=50)
        self.fraud_detector = FraudDetector()

        # Clear files
        if os.path.exists(self.accounts_file):
            os.remove(self.accounts_file)
        if os.path.exists(self.transactions_file):
            os.remove(self.transactions_file)

        return True, "System reset successfully!"
