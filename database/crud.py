import pandas as pd
from sqlalchemy import text
from database.connection import get_engine

def get_all_products():
    engine = get_engine()
    query = """
        SELECT ProductID, SKU, ProductName, CategoryName, BasePrice, TotalStock 
        FROM vw_InventoryStatus 
        ORDER BY ProductID DESC
    """
    return pd.read_sql(query, engine)

def add_product(sku, name, category_id, supplier_id, price):
    """Створює лише картку товару (без залишків)"""
    engine = get_engine()
    query = text("""
        INSERT INTO Dim_Products (SKU, ProductName, CategoryID, SupplierID, BasePrice, IsPrescription)
        VALUES (:sku, :name, :cat, :sup, :price, 0)
    """)
    with engine.begin() as conn:
        conn.execute(query, {"sku": sku, "name": name, "cat": category_id, "sup": supplier_id, "price": price})

def restock_product(product_id, pharmacy_id, quantity):
    """Поповнює залишки існуючого товару на складі"""
    engine = get_engine()
    query = text("""
        IF EXISTS (SELECT 1 FROM Fact_Inventory WHERE ProductID = :pid AND PharmacyID = :phid)
            UPDATE Fact_Inventory 
            SET StockQuantity = StockQuantity + :qty 
            WHERE ProductID = :pid AND PharmacyID = :phid
        ELSE
            -- Додаємо ще й SnapshotDate та передаємо GETDATE()
            INSERT INTO Fact_Inventory (ProductID, PharmacyID, StockQuantity, ExpirationDate, SnapshotDate) 
            VALUES (:pid, :phid, :qty, DATEADD(year, 1, GETDATE()), GETDATE())
    """)
    with engine.begin() as conn:
        conn.execute(query, {"pid": product_id, "phid": pharmacy_id, "qty": quantity})

def process_sale(product_id, pharmacy_id, quantity, price):
    engine = get_engine()
    query = text("EXEC sp_ProcessSale @ProductID=:pid, @PharmacyID=:phid, @Quantity=:qty, @ActualPrice=:price")
    with engine.begin() as conn:
        conn.execute(query, {"pid": product_id, "phid": pharmacy_id, "qty": quantity, "price": price})