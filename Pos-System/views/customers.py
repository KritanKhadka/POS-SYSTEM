import customtkinter as ctk
from database import SessionLocal
import models
from decimal import Decimal


class CustomersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = SessionLocal()
        self.selected_customer = None
        self.build_ui()

    def build_ui(self):
        # ── Left Panel ──────────────────────────
        self.left = ctk.CTkFrame(self, width=300)
        self.left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.left, text="Customers",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Search bar
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_customers)
        ctk.CTkEntry(self.left, placeholder_text="Search customer...",
                     textvariable=self.search_var).pack(padx=10, fill="x")

        # Customer list
        self.customer_list = ctk.CTkScrollableFrame(self.left)
        self.customer_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Add customer button
        ctk.CTkButton(self.left, text="+ Add Customer",
                      command=self.open_add_customer).pack(padx=10, pady=10, fill="x")

        # ── Right Panel ─────────────────────────
        self.right = ctk.CTkFrame(self)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.detail_label = ctk.CTkLabel(
            self.right,
            text="Select a customer to view details",
            font=ctk.CTkFont(size=14)
        )
        self.detail_label.pack(pady=20)

        self.load_customers()

    def load_customers(self, search=""):
        for w in self.customer_list.winfo_children():
            w.destroy()

        customers = self.db.query(models.Customer)
        if search:
            customers = customers.filter(
                models.Customer.name.ilike(f"%{search}%")
            )
        customers = customers.all()

        for c in customers:
            color = "#FF4444" if float(c.total_owed or 0) > 0 else "#44AA44"
            btn = ctk.CTkButton(
                self.customer_list,
                text=f"{c.name}\nOwes: Rs.{c.total_owed or 0}",
                fg_color=color,
                anchor="w",
                command=lambda cust=c: self.show_customer(cust)
            )
            btn.pack(fill="x", pady=3)

    def filter_customers(self, *args):
        self.load_customers(self.search_var.get())

    def show_customer(self, customer):
        # Refresh customer from DB to get latest data
        self.db.refresh(customer)
        self.selected_customer = customer

        for w in self.right.winfo_children():
            w.destroy()

        # ── Customer Name & Info ─────────────────
        ctk.CTkLabel(self.right, text=customer.name,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(
            self.right,
            text=f"📍 {customer.location or 'N/A'}   📞 {customer.phone or 'N/A'}",
            font=ctk.CTkFont(size=13)
        ).pack()

        # ── Balance Frame ────────────────────────
        bal_frame = ctk.CTkFrame(self.right)
        bal_frame.pack(pady=15, padx=20, fill="x")

        ctk.CTkLabel(
            bal_frame,
            text=f"Total Owed:  Rs. {customer.total_owed or 0}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FF4444"
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            bal_frame,
            text=f"Total Paid:  Rs. {customer.total_paid or 0}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#44AA44"
        ).pack(side="right", padx=20, pady=10)

        # ── Action Buttons ───────────────────────
        btn_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame, text="Record Payment",
            fg_color="#44AA44",
            command=lambda: self.open_payment(customer)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Edit Customer",
            fg_color="#888888",
            command=lambda: self.open_edit_customer(customer)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Delete Customer",
            fg_color="#FF4444",
            command=lambda: self.delete_customer(customer)
        ).pack(side="left", padx=10)

        # ── Transaction History ──────────────────
        ctk.CTkLabel(self.right, text="Transaction History",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 5))

        history = ctk.CTkScrollableFrame(self.right)
        history.pack(fill="both", expand=True, padx=20, pady=5)

        txns = self.db.query(models.TransactionRecord).filter(
            models.TransactionRecord.customer_id == customer.id
        ).order_by(models.TransactionRecord.created_at.desc()).all()

        if not txns:
            ctk.CTkLabel(history, text="No transactions yet.").pack(pady=10)
        else:
            for t in txns:
                if t.transaction_type == "payment":
                    color = "#44AA44"
                elif t.transaction_type == "opening_balance":
                    color = "#AAAAAA"
                else:
                    color = "#FF4444"

                date_str = t.created_at.strftime('%b %d, %Y') if t.created_at else "N/A"

                ctk.CTkLabel(
                    history,
                    text=f"{date_str}  |  {t.transaction_type.upper()}  |  "
                         f"Paid: Rs.{t.amount_paid}  |  Balance: Rs.{t.balance_after}",
                    text_color=color
                ).pack(anchor="w", pady=2, padx=5)

    # ── Add Customer ─────────────────────────────
    def open_add_customer(self):
        win = ctk.CTkToplevel(self)
        win.title("Add Customer")
        win.geometry("400x420")
        win.grab_set()

        ctk.CTkLabel(win, text="Add New Customer",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        name_entry = ctk.CTkEntry(win, placeholder_text="Full Name")
        name_entry.pack(padx=30, pady=5, fill="x")

        phone_entry = ctk.CTkEntry(win, placeholder_text="Phone Number")
        phone_entry.pack(padx=30, pady=5, fill="x")

        location_entry = ctk.CTkEntry(win, placeholder_text="Location / Address")
        location_entry.pack(padx=30, pady=5, fill="x")

        opening_balance_entry = ctk.CTkEntry(
            win,
            placeholder_text="Opening Balance (Rs.) - if they already owe"
        )
        opening_balance_entry.pack(padx=30, pady=5, fill="x")

        msg = ctk.CTkLabel(win, text="")
        msg.pack(pady=5)

        def save():
            name = name_entry.get().strip()
            if not name:
                msg.configure(text="Name is required!", text_color="red")
                return

            try:
                opening_balance = float(opening_balance_entry.get().strip() or 0)
            except:
                opening_balance = 0

            customer = models.Customer(
                name       = name,
                phone      = phone_entry.get().strip(),
                location   = location_entry.get().strip(),
                total_owed = opening_balance,
                total_paid = 0
            )
            self.db.add(customer)
            self.db.flush()

            # Log opening balance as transaction if exists
            if opening_balance > 0:
                txn = models.TransactionRecord(
                    customer_id      = customer.id,
                    customer_name    = customer.name,
                    transaction_type = "opening_balance",
                    total_amount     = opening_balance,
                    amount_paid      = 0,
                    amount_remaining = opening_balance,
                    balance_before   = 0,
                    balance_after    = opening_balance,
                    note             = "Opening balance on registration"
                )
                self.db.add(txn)

            self.db.commit()
            msg.configure(text="Customer added!", text_color="green")
            self.load_customers()
            win.after(1000, win.destroy)

        ctk.CTkButton(win, text="Save Customer", command=save).pack(pady=15)

    # ── Edit Customer ────────────────────────────
    def open_edit_customer(self, customer):
        win = ctk.CTkToplevel(self)
        win.title("Edit Customer")
        win.geometry("400x350")
        win.grab_set()

        ctk.CTkLabel(win, text="Edit Customer",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        name_entry = ctk.CTkEntry(win, placeholder_text="Full Name")
        name_entry.insert(0, customer.name or "")
        name_entry.pack(padx=30, pady=5, fill="x")

        phone_entry = ctk.CTkEntry(win, placeholder_text="Phone Number")
        phone_entry.insert(0, customer.phone or "")
        phone_entry.pack(padx=30, pady=5, fill="x")

        location_entry = ctk.CTkEntry(win, placeholder_text="Location / Address")
        location_entry.insert(0, customer.location or "")
        location_entry.pack(padx=30, pady=5, fill="x")

        msg = ctk.CTkLabel(win, text="")
        msg.pack(pady=5)

        def save():
            customer.name     = name_entry.get().strip()
            customer.phone    = phone_entry.get().strip()
            customer.location = location_entry.get().strip()
            self.db.commit()
            msg.configure(text="Updated!", text_color="green")
            self.load_customers()
            self.show_customer(customer)
            win.after(1000, win.destroy)

        ctk.CTkButton(win, text="Save Changes", command=save).pack(pady=15)

    # ── Record Payment ───────────────────────────
    def open_payment(self, customer):
        win = ctk.CTkToplevel(self)
        win.title("Record Payment")
        win.geometry("400x320")
        win.grab_set()

        ctk.CTkLabel(win, text=f"Payment from {customer.name}",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(
            win,
            text=f"Currently Owes: Rs. {customer.total_owed or 0}",
            text_color="#FF4444"
        ).pack()

        amount_entry = ctk.CTkEntry(win, placeholder_text="Amount Received (Rs.)")
        amount_entry.pack(padx=30, pady=15, fill="x")

        note_entry = ctk.CTkEntry(win, placeholder_text="Note (optional)")
        note_entry.pack(padx=30, pady=5, fill="x")

        msg = ctk.CTkLabel(win, text="")
        msg.pack(pady=5)

        def save():
            try:
                amount = Decimal(amount_entry.get().strip())
            except:
                msg.configure(text="Enter a valid amount!", text_color="red")
                return

            balance_before = Decimal(str(customer.total_owed or 0))
            balance_after  = balance_before - amount

            # Update customer balances
            customer.total_owed = float(balance_after)
            customer.total_paid = float(
                Decimal(str(customer.total_paid or 0)) + amount
            )

            # Log transaction
            txn = models.TransactionRecord(
                customer_id      = customer.id,
                customer_name    = customer.name,
                transaction_type = "payment",
                total_amount     = float(balance_before),
                amount_paid      = float(amount),
                amount_remaining = float(balance_after),
                balance_before   = float(balance_before),
                balance_after    = float(balance_after),
                note             = note_entry.get().strip()
            )
            self.db.add(txn)
            self.db.commit()

            msg.configure(text="Payment recorded!", text_color="green")
            self.load_customers()
            self.show_customer(customer)
            win.after(1000, win.destroy)

        ctk.CTkButton(
            win, text="Record Payment",
            fg_color="#44AA44",
            command=save
        ).pack(pady=15)

    # ── Delete Customer ──────────────────────────
    def delete_customer(self, customer):
        win = ctk.CTkToplevel(self)
        win.title("Delete Customer")
        win.geometry("380x220")
        win.grab_set()

        owes = float(customer.total_owed or 0)

        if owes > 0:
            ctk.CTkLabel(
                win,
                text=f"⚠️ {customer.name} still owes Rs. {owes}!",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FF4444"
            ).pack(pady=(20, 5))
            ctk.CTkLabel(
                win,
                text="Are you sure you want to delete?\nTransaction records will be kept.",
                text_color="#AAAAAA"
            ).pack(pady=5)
        else:
            ctk.CTkLabel(
                win,
                text=f"Delete '{customer.name}'?",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(pady=(20, 5))
            ctk.CTkLabel(
                win,
                text="Transaction records will be kept.",
                text_color="#AAAAAA"
            ).pack(pady=5)

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=20)

        def confirm():
            # Preserve history by unlinking customer_id
            self.db.query(models.TransactionRecord).filter(
                models.TransactionRecord.customer_id == customer.id
            ).update({"customer_id": None})

            self.db.query(models.ProductsBoughtRecord).filter(
                models.ProductsBoughtRecord.customer_id == customer.id
            ).update({"customer_id": None})

            self.db.delete(customer)
            self.db.commit()

            # Clear right panel
            for w in self.right.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.right,
                text="Select a customer to view details",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)

            self.load_customers()
            win.destroy()

        ctk.CTkButton(
            btn_frame, text="Yes, Delete",
            fg_color="#FF4444", command=confirm
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Cancel",
            fg_color="#555555",
            command=win.destroy
        ).pack(side="left", padx=10)