import tkinter as tk
from tkinter import ttk
from db_tools import * 
from playsound import playsound
from PIL import Image, ImageTk
import threading



class TransactionViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Transaction Viewer")
        self.root.geometry("1200x600")
        self.tls = self  
        self.db = init_with_db("mysql")

        self.logo_frame = tk.Frame(root)
        self.logo_frame.pack(pady=10)

        self.display_logo()

        self.transactions_frame = tk.LabelFrame(root, text="Transactions", padx=10, pady=10)
        self.transactions_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.clients_frame = tk.LabelFrame(root, text="Clients", padx=10, pady=10)
        self.clients_frame.pack(fill="both", expand=True, padx=10, pady=5)
        

        background_thread = threading.Thread(target=self.background_music, daemon=True)
        background_thread.start()
        

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



    def display_logo(self):
        # Load and display the image
        image = Image.open("logo.jpg")  # Your uploaded file path
        image = image.resize((200, 200))  # Resize if needed
        self.logo_image = ImageTk.PhotoImage(image)
        
        logo_label = tk.Label(self.logo_frame, image=self.logo_image)
        logo_label.pack()

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
        if table_name=="transactions":
            columns=["primary_trans_id" , "secondary_trans_id" , "client_id" , "timestamp" , "data_size" , "data"]
        if table_name=="clients":
            columns=["client_id" , "ip" , "port" , "ddos_status" , "timestamp"]

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
        self.db = init_with_db("mysql")  
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
        self.root.after(5000, self.schedule_refresh) 
    
    def background_music(self):
        playsound('elevator_music.wav')

if __name__ == "__main__":
    root = tk.Tk()
    viewer = TransactionViewer(root)
    root.mainloop()






