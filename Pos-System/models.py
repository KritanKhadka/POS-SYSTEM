from sqlalchemy import Column, Integer, String, Numeric, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from database import Base


class Customer(Base):
    __tablename__ = "customers"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    phone      = Column(String)
    location   = Column(Text)
    total_owed = Column(Numeric(12, 2), default=0)
    total_paid = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False)
    category    = Column(String)
    fixed_price = Column(Numeric(10, 2), nullable=False)
    cost_price  = Column(Numeric(10, 2))
    image_url   = Column(Text)
    created_at  = Column(DateTime, server_default=func.now())


class Inventory(Base):
    __tablename__ = "inventory"
    id             = Column(Integer, primary_key=True, index=True)
    product_id     = Column(Integer, ForeignKey("products.id"))
    stock          = Column(Integer, default=0)
    alert_level    = Column(Integer, default=10)
    last_restocked = Column(DateTime)


class Sale(Base):
    __tablename__ = "sales"
    id           = Column(Integer, primary_key=True, index=True)
    customer_id  = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Numeric(12, 2))
    amount_paid  = Column(Numeric(12, 2))
    remaining    = Column(Numeric(12, 2))
    sale_date    = Column(DateTime, server_default=func.now())


class SaleItem(Base):
    __tablename__ = "sale_items"
    id            = Column(Integer, primary_key=True, index=True)
    sale_id       = Column(Integer, ForeignKey("sales.id"))
    product_id    = Column(Integer, ForeignKey("products.id"))
    quantity      = Column(Integer)
    fixed_price   = Column(Numeric(10, 2))
    unit_price    = Column(Numeric(10, 2))
    is_overridden = Column(Boolean, default=False)
    subtotal      = Column(Numeric(10, 2))


class ProductsBoughtRecord(Base):
    __tablename__ = "products_bought_record"
    id            = Column(Integer, primary_key=True, index=True)
    customer_id   = Column(Integer, ForeignKey("customers.id"))
    customer_name = Column(String)
    product_id    = Column(Integer, ForeignKey("products.id"))
    product_name  = Column(String)
    quantity      = Column(Integer)
    fixed_price   = Column(Numeric(10, 2))
    unit_price    = Column(Numeric(10, 2))
    is_overridden = Column(Boolean, default=False)
    subtotal      = Column(Numeric(10, 2))
    sale_id       = Column(Integer, ForeignKey("sales.id"))
    bought_at     = Column(DateTime, server_default=func.now())


class TransactionRecord(Base):
    __tablename__ = "transactions_record"
    id               = Column(Integer, primary_key=True, index=True)
    customer_id      = Column(Integer, ForeignKey("customers.id"))
    customer_name    = Column(String)
    transaction_type = Column(String)
    total_amount     = Column(Numeric(12, 2))
    amount_paid      = Column(Numeric(12, 2))
    amount_remaining = Column(Numeric(12, 2))
    balance_before   = Column(Numeric(12, 2))
    balance_after    = Column(Numeric(12, 2))
    note             = Column(Text)
    reference_id     = Column(Integer)
    created_at       = Column(DateTime, server_default=func.now())


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey("products.id"))
    transaction_type = Column(String)   # 'restock', 'sale', 'adjustment', 'damage'
    quantity_change  = Column(Integer)  # positive = added, negative = removed
    stock_before     = Column(Integer)
    stock_after      = Column(Integer)
    note             = Column(Text)
    created_at       = Column(DateTime, server_default=func.now())