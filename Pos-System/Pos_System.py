import customtkinter as ctk
from database import engine
import models

# Create all tables automatically
models.Base.metadata.create_all(bind=engine)

# App settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POS System")
        self.geometry("1200x700")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(
            self.sidebar,
            text="POS SYSTEM",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        # Sidebar buttons
        buttons = ["Customers", "Products", "Inventory", "Sales", "Transactions"]
        for btn in buttons:
            ctk.CTkButton(
                self.sidebar,
                text=btn,
                command=lambda b=btn: self.load_view(b)
            ).pack(pady=8, padx=10, fill="x")

        # Main content area
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Load default screen
        self.load_view("Customers")

    def load_view(self, view_name):
        for widget in self.content.winfo_children():
            widget.destroy()

        if view_name == "Customers":
            from views.customers import CustomersView
            view = CustomersView(self.content)
            view.pack(fill="both", expand=True)
        elif view_name == "Products":
            from views.products import ProductsView
            view = ProductsView(self.content)
            view.pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(
                self.content,
                text=f"{view_name} — Coming Soon",
                font=ctk.CTkFont(size=22, weight="bold")
            ).pack(pady=20)

            ctk.CTkLabel(
                self.content,
                text=f"{view_name}",
                font=ctk.CTkFont(size=22, weight="bold")
            ).pack(pady=20)

        ctk.CTkLabel(
            self.content,
            text="Loading...",
            font=ctk.CTkFont(size=14)
        ).pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()
