import customtkinter as ctk
from database import SessionLocal
import models
import os
from PIL import Image

class ProductsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = SessionLocal()
        self.selected_product = None
        self.build_ui()

    def build_ui(self):
        # ── Left Panel ──────────────────────────
        self.left = ctk.CTkFrame(self, width=300)
        self.left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.left, text="Products",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_products)
        ctk.CTkEntry(self.left, placeholder_text="Search product...",
                     textvariable=self.search_var).pack(padx=10, fill="x")

        # Category filter
        self.category_var = ctk.StringVar(value="All")
        self.category_menu = ctk.CTkOptionMenu(
            self.left,
            variable=self.category_var,
            values=["All"],
            command=self.filter_products
        )
        self.category_menu.pack(padx=10, pady=5, fill="x")

        # Product list
        self.product_list = ctk.CTkScrollableFrame(self.left)
        self.product_list.pack(fill="both", expand=True, padx=10, pady=5)

        # Add product button
        ctk.CTkButton(self.left, text="+ Add Product",
                      command=self.open_add_product).pack(padx=10, pady=10, fill="x")

        # ── Right Panel ─────────────────────────
        self.right = ctk.CTkFrame(self)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.right,
                     text="Select a product to view details",
                     font=ctk.CTkFont(size=14)).pack(pady=20)

        self.load_products()

    def load_products(self, search="", category="All"):
        for w in self.product_list.winfo_children():
            w.destroy()

        products = self.db.query(models.Product)

        if search:
            products = products.filter(
                models.Product.name.ilike(f"%{search}%")
            )
        if category != "All":
            products = products.filter(
                models.Product.category == category
            )

        products = products.all()

        # Update category dropdown
        all_cats = self.db.query(models.Product.category).distinct().all()
        cats = ["All"] + [c[0] for c in all_cats if c[0]]
        self.category_menu.configure(values=cats)

        for p in products:
            btn = ctk.CTkButton(
                self.product_list,
                text=f"{p.name}\nRs. {p.fixed_price}  |  {p.category or 'Uncategorized'}",
                anchor="w",
                command=lambda prod=p: self.show_product(prod)
            )
            btn.pack(fill="x", pady=3)

    def filter_products(self, *args):
        self.load_products(
            search=self.search_var.get(),
            category=self.category_var.get()
        )

    def show_product(self, product):
        self.selected_product = product

        for w in self.right.winfo_children():
            w.destroy()

        # Product image
        if product.image_url and os.path.exists(product.image_url):
            img = Image.open(product.image_url)
            img = img.resize((180, 180))
            ctk_img = ctk.CTkImage(light_image=img, size=(180, 180))
            ctk.CTkLabel(self.right, image=ctk_img, text="").pack(pady=(20, 5))
        else:
            ctk.CTkLabel(self.right, text="🖼️ No Image",
                         font=ctk.CTkFont(size=40)).pack(pady=(20, 5))

        # Product name
        ctk.CTkLabel(self.right, text=product.name,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(5, 2))

        ctk.CTkLabel(self.right,
                     text=f"Category: {product.category or 'Uncategorized'}",
                     font=ctk.CTkFont(size=13)).pack()

        # Price frame
        price_frame = ctk.CTkFrame(self.right)
        price_frame.pack(pady=15, padx=20, fill="x")

        ctk.CTkLabel(price_frame,
                     text=f"Fixed Price:  Rs. {product.fixed_price}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#4DA6FF").pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(price_frame,
                     text=f"Cost Price:  Rs. {product.cost_price or 'N/A'}",
                     font=ctk.CTkFont(size=14),
                     text_color="#AAAAAA").pack(side="right", padx=20, pady=10)

        # Stock info
        inventory = self.db.query(models.Inventory).filter(
            models.Inventory.product_id == product.id
        ).first()

        if inventory:
            stock_color = "#FF4444" if inventory.stock <= inventory.alert_level else "#44AA44"
            ctk.CTkLabel(self.right,
                         text=f"Stock: {inventory.stock} units",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=stock_color).pack(pady=5)
            if inventory.stock <= inventory.alert_level:
                ctk.CTkLabel(self.right, text="⚠️ Low Stock!",
                             text_color="#FF4444").pack()
        else:
            ctk.CTkLabel(self.right, text="Stock: Not tracked",
                         text_color="#AAAAAA").pack(pady=5)

        # Action buttons
        btn_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Edit Product",
                      fg_color="#888888",
                      command=lambda: self.open_edit_product(product)).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Delete Product",
                      fg_color="#FF4444",
                      command=lambda: self.delete_product(product)).pack(side="left", padx=10)

    def open_add_product(self):
        win = ctk.CTkToplevel(self)
        win.title("Add Product")
        win.geometry("420x500")
        win.grab_set()

        ctk.CTkLabel(win, text="Add New Product",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        name_entry = ctk.CTkEntry(win, placeholder_text="Product Name")
        name_entry.pack(padx=30, pady=5, fill="x")

        category_entry = ctk.CTkEntry(win, placeholder_text="Category (e.g. Groceries)")
        category_entry.pack(padx=30, pady=5, fill="x")

        price_entry = ctk.CTkEntry(win, placeholder_text="Fixed Price (Rs.)")
        price_entry.pack(padx=30, pady=5, fill="x")

        cost_entry = ctk.CTkEntry(win, placeholder_text="Cost Price (Rs.) - optional")
        cost_entry.pack(padx=30, pady=5, fill="x")

        stock_entry = ctk.CTkEntry(win, placeholder_text="Initial Stock")
        stock_entry.pack(padx=30, pady=5, fill="x")

        alert_entry = ctk.CTkEntry(win, placeholder_text="Low Stock Alert Level (default 10)")
        alert_entry.pack(padx=30, pady=5, fill="x")

        # Image picker
        self.image_path = None
        img_label = ctk.CTkLabel(win, text="No image selected", text_color="#AAAAAA")
        img_label.pack(pady=3)

        def pick_image():
            from tkinter import filedialog
            path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")]
            )
            if path:
                self.image_path = path
                img_label.configure(
                    text=os.path.basename(path),
                    text_color="green"
                )

        ctk.CTkButton(win, text="📷 Upload Image",
                      fg_color="#555555",
                      command=pick_image).pack(padx=30, pady=3, fill="x")

        msg = ctk.CTkLabel(win, text="")
        msg.pack(pady=5)

        def save():
            name = name_entry.get().strip()
            if not name:
                msg.configure(text="Product name required!", text_color="red")
                return
            try:
                price = float(price_entry.get().strip())
            except:
                msg.configure(text="Enter a valid price!", text_color="red")
                return

            cost = None
            if cost_entry.get().strip():
                try:
                    cost = float(cost_entry.get().strip())
                except:
                    msg.configure(text="Enter a valid cost price!", text_color="red")
                    return

            # Save product
            product = models.Product(
                name        = name,
                category    = category_entry.get().strip() or None,
                fixed_price = price,
                cost_price  = cost,
                image_url   = self.image_path
            )
            self.db.add(product)
            self.db.flush()

            # Save inventory
            try:
                stock = int(stock_entry.get().strip())
            except:
                stock = 0
            try:
                alert = int(alert_entry.get().strip())
            except:
                alert = 10

            inventory = models.Inventory(
                product_id  = product.id,
                stock       = stock,
                alert_level = alert
            )
            self.db.add(inventory)
            self.db.commit()

            msg.configure(text="Product added!", text_color="green")
            self.load_products()
            win.after(1000, win.destroy)

        ctk.CTkButton(win, text="Save Product", command=save).pack(pady=10)

    def open_edit_product(self, product):
        win = ctk.CTkToplevel(self)
        win.title("Edit Product")
        win.geometry("420x450")
        win.grab_set()

        ctk.CTkLabel(win, text="Edit Product",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

        name_entry = ctk.CTkEntry(win, placeholder_text="Product Name")
        name_entry.insert(0, product.name or "")
        name_entry.pack(padx=30, pady=5, fill="x")

        category_entry = ctk.CTkEntry(win, placeholder_text="Category")
        category_entry.insert(0, product.category or "")
        category_entry.pack(padx=30, pady=5, fill="x")

        price_entry = ctk.CTkEntry(win, placeholder_text="Fixed Price")
        price_entry.insert(0, str(product.fixed_price or ""))
        price_entry.pack(padx=30, pady=5, fill="x")

        cost_entry = ctk.CTkEntry(win, placeholder_text="Cost Price")
        cost_entry.insert(0, str(product.cost_price or ""))
        cost_entry.pack(padx=30, pady=5, fill="x")

        msg = ctk.CTkLabel(win, text="")
        msg.pack(pady=5)

        def save():
            try:
                price = float(price_entry.get().strip())
            except:
                msg.configure(text="Enter a valid price!", text_color="red")
                return

            # Log price change if price changed
            if float(product.fixed_price) != price:
                history = models.price_history(
                    product_id = product.id,
                    old_price  = float(product.fixed_price),
                    new_price  = price,
                    note       = "Manual price update"
                )
                self.db.add(history)

            product.name        = name_entry.get().strip()
            product.category    = category_entry.get().strip() or None
            product.fixed_price = price
            product.cost_price  = float(cost_entry.get().strip()) if cost_entry.get().strip() else None

            self.db.commit()
            msg.configure(text="Product updated!", text_color="green")
            self.load_products()
            self.show_product(product)
            win.after(1000, win.destroy)

        ctk.CTkButton(win, text="Save Changes", command=save).pack(pady=15)

    def delete_product(self, product):
        win = ctk.CTkToplevel(self)
        win.title("Confirm Delete")
        win.geometry("350x180")
        win.grab_set()

        ctk.CTkLabel(win,
                     text=f"Delete '{product.name}'?",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=20)
        ctk.CTkLabel(win, text="This cannot be undone.",
                     text_color="#FF4444").pack()

        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=20)

        def confirm():
            self.db.query(models.Inventory).filter(
                models.Inventory.product_id == product.id
            ).delete()
            self.db.delete(product)
            self.db.commit()

            for w in self.right.winfo_children():
                w.destroy()
            ctk.CTkLabel(self.right,
                         text="Select a product to view details",
                         font=ctk.CTkFont(size=14)).pack(pady=20)

            self.load_products()
            win.destroy()

        ctk.CTkButton(btn_frame, text="Yes, Delete",
                      fg_color="#FF4444", command=confirm).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel",
                      fg_color="#555555", command=win.destroy).pack(side="left", padx=10)
