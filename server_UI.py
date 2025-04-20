import tkinter as tk
from tkinter import ttk
from db_tools import *  # Assuming this is from your project

class TransactionViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Viewer")
        self.root.geometry("1200x600")
        self.tls = self  # Temporary adapter for calling get_all_rows
        self.db = init_with_db("mysql")

        # Set up frames
        self.transactions_frame = tk.LabelFrame(root, text="Transactions", padx=10, pady=10)
        self.transactions_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.clients_frame = tk.LabelFrame(root, text="Clients", padx=10, pady=10)
        self.clients_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Initialize tables with try/except for debugging
        try:
            self.transactions_tree = self.create_table(self.transactions_frame, "transactions")
        except Exception as e:
            print("Error creating transactions table:", e)
            self.transactions_tree = None

        try:
            self.clients_tree = self.create_table(self.clients_frame, "clients")
        except Exception as e:
            print("Error creating clients table:", e)
            self.clients_tree = None

        print("Init complete. Starting refresh loop...")
        self.schedule_refresh()

    def get_all_rows(self, db, table):
        try:
            rows = get_all_rows(db, table)
            print(f"Fetched {len(rows)} rows from {table}")
            return rows
        except Exception as e:
            print(f"Error fetching rows from {table}:", e)
            return []

    def create_table(self, parent_frame, table_name):
        sample_data = self.tls.get_all_rows(self.db, table_name)
        columns = [f"Column {i+1}" for i in range(len(sample_data[0]))] if sample_data else ["No Data"]

        tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        return tree

    def refresh_table(self, tree, table_name):
        print(f"Refreshing table: {table_name}")
        self.db = init_with_db("mysql")  # Reconnect to DB each time
        for item in tree.get_children():
            tree.delete(item)

        updated_rows = self.tls.get_all_rows(self.db, table_name)
        for row in updated_rows:
            tree.insert("", "end", values=row)

    def schedule_refresh(self):
        print("Scheduled refresh running...")
        if self.transactions_tree:
            self.refresh_table(self.transactions_tree, "transactions")
        if self.clients_tree:
            self.refresh_table(self.clients_tree, "clients")
        self.root.after(5000, self.schedule_refresh)  # Refresh every 5 seconds

if __name__ == "__main__":
    root = tk.Tk()
    viewer = TransactionViewer(root)
    root.mainloop()






