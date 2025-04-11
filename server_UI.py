import tkinter as tk
from tkinter import ttk
from db_tools import *  # Assuming this is from your project

class TransactionViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Viewer")
        self.root.geometry("900x400")
        self.tls = self  # Temporary adapter for calling get_all_rows
        self.db = init_with_db("mysql")

        self.transactions_tree = self.show_transactions(self.root, self.db)

        # Add refresh button
        refresh_button = tk.Button(self.root, text="Refresh", command=lambda: self.refresh_transactions_table(self.db))
        refresh_button.pack(pady=10)

    def get_all_rows(self, db, table):
        return get_all_rows(db, table)

    def show_transactions(self, root, mydb):
        transactions_label = tk.Label(root, text="Transactions", font=("Helvetica", 16, "bold"))
        transactions_label.pack(anchor="n", pady=10)

        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("Primary ID", "Secondary ID", "Client ID", "Timestamp", "Data Size", "Data")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        # Fetch data from MySQL and insert
        transactions = self.tls.get_all_rows(mydb, "transactions")
        for t in transactions:
            tree.insert("", "end", values=t)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        return tree

    def refresh_transactions_table(self, mydb):
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)

        updated_transactions = self.tls.get_all_rows(mydb, "transactions")
        for transaction in updated_transactions:
            self.transactions_tree.insert("", "end", values=transaction)


if __name__ == "__main__":
    root = tk.Tk()
    viewer = TransactionViewer(root)
    root.mainloop()


