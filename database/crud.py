import pandas as pd
import hashlib
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


def hash_password(password):
    """Шифрує пароль за алгоритмом SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def create_user(username, password, role="Фармацевт"):
    """Реєструє нового користувача в базі даних (використовувати тільки адміну)"""
    engine = get_engine()
    hashed_pw = hash_password(password)
    query = text("INSERT INTO Dim_Users (Username, PasswordHash, Role) VALUES (:user, :hash, :role)")
    with engine.begin() as conn:
        conn.execute(query, {"user": username, "hash": hashed_pw, "role": role})


def verify_login(username, password):
    """Перевіряє, чи співпадає пароль з тим, що у базі"""
    engine = get_engine()
    query = text("SELECT PasswordHash, Role FROM Dim_Users WHERE Username = :user")

    with engine.connect() as conn:
        result = conn.execute(query, {"user": username}).fetchone()

        # Якщо користувач знайдений
        if result:
            stored_hash = result[0]
            # Порівнюємо хеші
            if stored_hash == hash_password(password):
                return True  # Авторизація успішна
    return False  # Неправильний логін або пароль