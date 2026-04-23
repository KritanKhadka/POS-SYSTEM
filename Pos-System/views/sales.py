import customtkinter as ctk
from database import SessionLocal
import models
from decimal import Decimal
from datetime import datetime


class SalesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = SessionLocal()
        self.cart = []
        self.selected_customer = None
        self.selected_product = None
        self.build_ui()

    def build_ui(self):
        # ── Left Panel — Customer + Product ─────
        self.left = ctk.CTkFrame(self, width=380)
        self.left.pack(side="left", fill="y", padx=10, pady=10)
        self.left.pack_propagate(False)

        ctk.CTkLabel(self.left, text="New Sale",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # ── Customer Selection ───────────────────
        ctk.CTkLabel(self.left, text="Select Customer:").pack(anchor="w", padx=10)

        cust_row = ctk.CTkFrame(self.left, fg_color="transparent")
        cust_row.pack(padx=10, fill="x")

        self.customer_search = ctk.CTkEntry(cust_row,
                                            placeholder_text="Search customer...")
        self.customer_search.pack(side="left", fill="x", expand=True)
        self.customer_search.bind("<KeyRelease>", self.filter_customers)

        ctk.CTkButton(
            cust_row, text="+ New",
            width=60, fg_color="#4DA6FF",
            command=self.quick_add_customer
        ).pack(side="left", padx=(5, 0))

        self.customer_dropdown = ctk.CTkScrollableFrame(self.left, height=100)
        self.customer_dropdown.pack(padx=10, fill="x")
        self.customer_dropdown.pack_forget()

        self.selected_customer_label = ctk.CTkLabel(
            self.left, text="No customer selected",
            text_color="#AAAAAA", font=ctk.CTkFont(size=12)
        )
        self.selected_customer_label.pack(padx=10, anchor="w")

        ctk.CTkFrame(self.left, height=1,
                     fg_color="#444444").pack(fill="x", padx=10, pady=10)

        # ── Product Selection ────────────────────
        ctk.CTkLabel(self.left, text="Add Product:").pack(anchor="w", padx=10)

        self.product_search = ctk.CTkEntry(self.left,
                                           placeholder_text="Search product...")
        self.product_search.pack(padx=10, fill="x")
        self.product_search.bind("<KeyRelease>", self.filter_products)

        self.product_dropdown = ctk.CTkScrollableFrame(self.left, height=120)
        self.product_dropdown.pack(padx=10, fill="x")
        self.product_dropdown.pack_forget()

        self.selected_product_label = ctk.CTkLabel(
            self.left, text="No product selected",
            text_color="#AAAAAA", font=ctk.CTkFont(size=12)
        )
        self.selected_product_label.pack(padx=10, anchor="w")

        # Quantity + Price
        qp_frame = ctk.CTkFrame(self.left, fg_color="transparent")
        qp_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(qp_frame, text="Qty:").pack(side="left")
        self.qty_entry = ctk.CTkEntry(qp_frame, width=70,
                                      placeholder_text="1")
        self.qty_entry.pack(side="left", padx=5)

        ctk.CTkLabel(qp_frame, text="Price (Rs.):").pack(side="left")
        self.price_entry = ctk.CTkEntry(qp_frame, width=100,
                                        placeholder_text="0.00")
        self.price_entry.pack(side="left", padx=5)

        self.add_msg = ctk.CTkLabel(self.left, text="",
                                    font=ctk.CTkFont(size=11))
        self.add_msg.pack(padx=10)

        ctk.CTkButton(self.left, text="+ Add to Cart",
                      fg_color="#4DA6FF",
                      command=self.add_to_cart).pack(padx=10, pady=8, fill="x")

        # ── Right Panel — Cart + Checkout ────────
        self.right = ctk.CTkFrame(self)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.right, text="Cart",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # Cart header
        header = ctk.CTkFrame(self.right)
        header.pack(fill="x", padx=10)
        for h, w in [("Product", 180), ("Qty", 60),
                     ("Fixed Rs.", 90), ("Charged Rs.", 100),
                     ("Subtotal", 90), ("", 60)]:
            ctk.CTkLabel(header, text=h, width=w,
                         font=ctk.CTkFont(weight="bold"),
                         anchor="w").pack(side="left", padx=3)

        # Cart items
        self.cart_frame = ctk.CTkScrollableFrame(self.right, height=260)
        self.cart_frame.pack(fill="x", padx=10, pady=5)

        # ── Totals ───────────────────────────────
        totals_frame = ctk.CTkFrame(self.right)
        totals_frame.pack(fill="x", padx=10, pady=5)

        self.total_label = ctk.CTkLabel(
            totals_frame, text="Total:  Rs. 0.00",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.total_label.pack(side="left", padx=20, pady=10)

        # Amount paying now
        pay_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        pay_frame.pack(fill="x", padx=10)

        ctk.CTkLabel(pay_frame, text="Amount Paying Now (Rs.):",
                     font=ctk.CTkFont(size=13)).pack(side="left", padx=10)
        self.paying_entry = ctk.CTkEntry(pay_frame, width=150,
                                         placeholder_text="0.00")
        self.paying_entry.pack(side="left", padx=5)
        self.paying_entry.bind("<KeyRelease>", self.update_remaining)

        self.remaining_label = ctk.CTkLabel(
            self.right, text="Remaining:  Rs. 0.00",
            font=ctk.CTkFont(size=13), text_color="#FF4444"
        )
        self.remaining_label.pack(padx=10, anchor="w")

        # Note
        note_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        note_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(note_frame, text="Note:").pack(side="left", padx=10)
        self.note_entry = ctk.CTkEntry(note_frame, width=300,
                                       placeholder_text="Optional note")
        self.note_entry.pack(side="left")

        self.checkout_msg = ctk.CTkLabel(self.right, text="")
        self.checkout_msg.pack()

        # Buttons
        btn_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="✅ Confirm Sale",
                      fg_color="#44AA44", width=160,
                      command=self.confirm_sale).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="🗑️ Clear Cart",
                      fg_color="#FF4444", width=120,
                      command=self.clear_cart).pack(side="left", padx=10)

    # ── Customer Search ──────────────────────────
    def filter_customers(self, event=None):
        search = self.customer_search.get().strip()
        for w in self.customer_dropdown.winfo_children():
            w.destroy()

        if not search:
            self.customer_dropdown.pack_forget()
            return

        customers = self.db.query(models.Customer).filter(
            models.Customer.name.ilike(f"%{search}%")
        ).all()

        if customers:
            self.customer_dropdown.pack(padx=10, fill="x")
            for c in customers:
                ctk.CTkButton(
                    self.customer_dropdown,
                    text=f"{c.name}  |  Owes: Rs.{c.total_owed or 0}",
                    anchor="w", height=30,
                    command=lambda cust=c: self.select_customer(cust)
                ).pack(fill="x", pady=1)
        else:
            self.customer_dropdown.pack_forget()

    def select_customer(self, customer):
        self.selected_customer = customer
        self.customer_search.delete(0, "end")
        self.customer_search.insert(0, customer.name)
        self.customer_dropdown.pack_forget()
        self.selected_customer_label.configure(
            text=f"✅ {customer.name}  |  Owes: Rs.{customer.total_owed or 0}",
            text_color="#44AA44"
        )

    # ── Quick Add Customer ───────────────────────
    def quick_add_customer(self):
        win = ctk.CTkToplevel(self)
        win.title("Quick Add Customer")
        win.geometry("400x380")
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
                opening_balance = float(
                    opening_balance_entry.get().strip() or 0
                )
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

            if opening_balance > 0:
                self.db.add(models.TransactionRecord(
                    customer_id      = customer.id,
                    customer_name    = customer.name,
                    transaction_type = "opening_balance",
                    total_amount     = opening_balance,
                    amount_paid      = 0,
                    amount_remaining = opening_balance,
                    balance_before   = 0,
                    balance_after    = opening_balance,
                    note             = "Opening balance on registration"
                ))

            self.db.commit()
            self.select_customer(customer)
            msg.configure(text="Customer added & selected!", text_color="green")
            win.after(1000, win.destroy)

        ctk.CTkButton(win, text="Save & Select Customer",
                      command=save).pack(pady=15)

    # ── Product Search ───────────────────────────
    def filter_products(self, event=None):
        search = self.product_search.get().strip()
        for w in self.product_dropdown.winfo_children():
            w.destroy()

        if not search:
            self.product_dropdown.pack_forget()
            return

        products = self.db.query(models.Product).filter(
            models.Product.name.ilike(f"%{search}%")
        ).all()

        if products:
            self.product_dropdown.pack(padx=10, fill="x")
            for p in products:
                inv = self.db.query(models.Inventory).filter(
                    models.Inventory.product_id == p.id
                ).first()
                stock = inv.stock if inv else 0
                ctk.CTkButton(
                    self.product_dropdown,
                    text=f"{p.name}  |  Rs.{p.fixed_price}  |  Stock: {stock}",
                    anchor="w", height=30,
                    command=lambda prod=p: self.select_product(prod)
                ).pack(fill="x", pady=1)
        else:
            self.product_dropdown.pack_forget()

    def select_product(self, product):
        self.selected_product = product
        self.product_search.delete(0, "end")
        self.product_search.insert(0, product.name)
        self.product_dropdown.pack_forget()
        self.selected_product_label.configure(
            text=f"✅ {product.name}  |  Fixed Price: Rs.{product.fixed_price}",
            text_color="#44AA44"
        )
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(product.fixed_price))

    # ── Cart ─────────────────────────────────────
    def add_to_cart(self):
        if not self.selected_product:
            self.add_msg.configure(text="Select a product first!",
                                   text_color="red")
            return

        try:
            qty = int(self.qty_entry.get().strip() or 1)
            if qty <= 0:
                raise ValueError
        except:
            self.add_msg.configure(text="Enter valid quantity!",
                                   text_color="red")
            return

        try:
            unit_price = float(self.price_entry.get().strip())
            if unit_price < 0:
                raise ValueError
        except:
            self.add_msg.configure(text="Enter valid price!",
                                   text_color="red")
            return

        inv = self.db.query(models.Inventory).filter(
            models.Inventory.product_id == self.selected_product.id
        ).first()

        if inv and inv.stock < qty:
            self.add_msg.configure(
                text=f"Not enough stock! Only {inv.stock} left.",
                text_color="red"
            )
            return

        fixed_price   = float(self.selected_product.fixed_price)
        subtotal      = qty * unit_price
        is_overridden = unit_price != fixed_price

        for item in self.cart:
            if item["product"].id == self.selected_product.id:
                item["quantity"]     += qty
                item["unit_price"]    = unit_price
                item["subtotal"]      = item["quantity"] * unit_price
                item["is_overridden"] = is_overridden
                self.refresh_cart()
                self.add_msg.configure(text="Cart updated!", text_color="green")
                return

        self.cart.append({
            "product":       self.selected_product,
            "quantity":      qty,
            "fixed_price":   fixed_price,
            "unit_price":    unit_price,
            "subtotal":      subtotal,
            "is_overridden": is_overridden
        })

        self.refresh_cart()
        self.add_msg.configure(text="Added to cart!", text_color="green")

        self.product_search.delete(0, "end")
        self.qty_entry.delete(0, "end")
        self.price_entry.delete(0, "end")
        self.selected_product = None
        self.selected_product_label.configure(
            text="No product selected", text_color="#AAAAAA"
        )

    def refresh_cart(self):
        for w in self.cart_frame.winfo_children():
            w.destroy()

        total = 0
        for i, item in enumerate(self.cart):
            row = ctk.CTkFrame(self.cart_frame)
            row.pack(fill="x", pady=2)

            override_color = "#FF8800" if item["is_overridden"] else "white"

            ctk.CTkLabel(row, text=item["product"].name,
                         width=180, anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(row, text=str(item["quantity"]),
                         width=60,  anchor="w").pack(side="left", padx=3)
            ctk.CTkLabel(row, text=f"Rs.{item['fixed_price']}",
                         width=90,  anchor="w",
                         text_color="#AAAAAA").pack(side="left", padx=3)
            ctk.CTkLabel(row, text=f"Rs.{item['unit_price']}",
                         width=100, anchor="w",
                         text_color=override_color).pack(side="left", padx=3)
            ctk.CTkLabel(row, text=f"Rs.{item['subtotal']:.2f}",
                         width=90,  anchor="w").pack(side="left", padx=3)

            ctk.CTkButton(
                row, text="✕", width=40, height=25,
                fg_color="#FF4444",
                command=lambda idx=i: self.remove_from_cart(idx)
            ).pack(side="left", padx=3)

            total += item["subtotal"]

        self.total_label.configure(text=f"Total:  Rs. {total:.2f}")
        self.update_remaining()

    def remove_from_cart(self, index):
        self.cart.pop(index)
        self.refresh_cart()

    def update_remaining(self, event=None):
        try:
            total     = sum(item["subtotal"] for item in self.cart)
            paying    = float(self.paying_entry.get().strip() or 0)
            remaining = total - paying
            color     = "#FF4444" if remaining > 0 else "#44AA44"
            self.remaining_label.configure(
                text=f"Remaining:  Rs. {remaining:.2f}",
                text_color=color
            )
        except:
            pass

    def clear_cart(self):
        self.cart = []
        self.refresh_cart()
        self.selected_customer = None
        self.selected_customer_label.configure(
            text="No customer selected", text_color="#AAAAAA"
        )
        self.customer_search.delete(0, "end")
        self.paying_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self.checkout_msg.configure(text="")

    # ── Confirm Sale ─────────────────────────────
    def confirm_sale(self):
        if not self.selected_customer:
            self.checkout_msg.configure(
                text="Select a customer first!", text_color="red"
            )
            return

        if not self.cart:
            self.checkout_msg.configure(
                text="Cart is empty!", text_color="red"
            )
            return

        try:
            paying = Decimal(self.paying_entry.get().strip() or "0")
        except:
            self.checkout_msg.configure(
                text="Enter a valid payment amount!", text_color="red"
            )
            return

        total     = Decimal(str(sum(item["subtotal"] for item in self.cart)))
        remaining = total - paying
        customer  = self.selected_customer

        self.db.refresh(customer)
        balance_before = Decimal(str(customer.total_owed or 0))
        balance_after  = balance_before + remaining

        # Create sale
        sale = models.Sale(
            customer_id  = customer.id,
            total_amount = float(total),
            amount_paid  = float(paying),
            remaining    = float(remaining),
            sale_date    = datetime.now()
        )
        self.db.add(sale)
        self.db.flush()

        for item in self.cart:
            product = item["product"]

            self.db.add(models.SaleItem(
                sale_id       = sale.id,
                product_id    = product.id,
                quantity      = item["quantity"],
                fixed_price   = item["fixed_price"],
                unit_price    = item["unit_price"],
                is_overridden = item["is_overridden"],
                subtotal      = item["subtotal"]
            ))

            self.db.add(models.ProductsBoughtRecord(
                customer_id   = customer.id,
                customer_name = customer.name,
                product_id    = product.id,
                product_name  = product.name,
                quantity      = item["quantity"],
                fixed_price   = item["fixed_price"],
                unit_price    = item["unit_price"],
                is_overridden = item["is_overridden"],
                subtotal      = item["subtotal"],
                sale_id       = sale.id,
                bought_at     = datetime.now()
            ))

            # Deduct inventory
            inv = self.db.query(models.Inventory).filter(
                models.Inventory.product_id == product.id
            ).first()
            if inv:
                stock_before = inv.stock or 0
                inv.stock    = stock_before - item["quantity"]
                self.db.add(models.InventoryTransaction(
                    product_id       = product.id,
                    transaction_type = "sale",
                    quantity_change  = -item["quantity"],
                    stock_before     = stock_before,
                    stock_after      = inv.stock,
                    note             = f"Sale ID {sale.id}"
                ))

        # Transaction record
        self.db.add(models.TransactionRecord(
            customer_id      = customer.id,
            customer_name    = customer.name,
            transaction_type = "sale",
            total_amount     = float(total),
            amount_paid      = float(paying),
            amount_remaining = float(remaining),
            balance_before   = float(balance_before),
            balance_after    = float(balance_after),
            note             = self.note_entry.get().strip(),
            reference_id     = sale.id
        ))

        # Update customer
        customer.total_owed = float(balance_after)
        customer.total_paid = float(
            Decimal(str(customer.total_paid or 0)) + paying
        )

        self.db.commit()

        self.checkout_msg.configure(
            text=f"✅ Sale saved! Total: Rs.{total}  "
                 f"Paid: Rs.{paying}  Remaining: Rs.{remaining}",
            text_color="green"
        )
        self.clear_cart()