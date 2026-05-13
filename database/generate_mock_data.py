import pandas as pd
from sqlalchemy import create_engine
import random
from datetime import datetime, timedelta

SERVER = 'localhost'
DATABASE = 'diploma'
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
engine = create_engine(CONNECTION_STRING)


def generate_data():
    print("Починаємо генерацію тестових даних...")

    categories = pd.DataFrame({'CategoryName': ['Антибіотики', 'Вітаміни та БАДи', 'Знеболювальні', 'Серцево-судинні',
                                                'Противірусні', 'Шлунково-кишкові']})
    suppliers = pd.DataFrame({
        'SupplierName': ['ТОВ БаДМ', 'СП Оптіма-Фарм', 'ПрАТ Дарниця', 'ПАТ Фармак'],
        'LeadTimeDays': [2, 1, 3, 2]
    })
    pharmacies = pd.DataFrame({
        'Address': ['вул. Хрещатик, 15', 'пр. Перемоги, 45', 'вул. Привокзальна, 1'],
        'PharmacyType': ['Цілодобова', 'Аптечний пункт', 'Класична']
    })

    categories.to_sql('Dim_Categories', engine, if_exists='append', index=False)
    suppliers.to_sql('Dim_Suppliers', engine, if_exists='append', index=False)
    pharmacies.to_sql('Dim_Pharmacies', engine, if_exists='append', index=False)
    print("Справочники завантажено.")

    cat_ids = pd.read_sql("SELECT CategoryID FROM Dim_Categories", engine)['CategoryID'].tolist()
    sup_ids = pd.read_sql("SELECT SupplierID FROM Dim_Suppliers", engine)['SupplierID'].tolist()
    pharm_ids = pd.read_sql("SELECT PharmacyID FROM Dim_Pharmacies", engine)['PharmacyID'].tolist()

    product_names = [
        'Амоксицилін 500 мг', 'Ібупрофен 400 мг', 'Парацетамол 500 мг', 'Німесил гранули',
        'Вітамін С 1000 мг', 'Магній В6 форте', 'Корвалмент капсули', 'Но-шпа 40 мг',
        'Фармацитрон пакетики', 'Аспірин Кардіо 100 мг', 'Пантестин мазь', 'Ентеросгель паста',
        'Мезим форте', 'Смекта порошок', 'Лоратадин 10 мг', 'Омепразол 20 мг',
        'Флюколд таблетки', 'Анальгін 500 мг', 'Валер’янка екстракт', 'Стрепсілс льодяники'
    ]

    products_data = []
    for i, name in enumerate(product_names):
        products_data.append({
            'SKU': f'SKU-{1000 + i}',
            'ProductName': name,
            'CategoryID': random.choice(cat_ids),
            'SupplierID': random.choice(sup_ids),
            'BasePrice': round(random.uniform(50.0, 500.0), 2),
            'IsPrescription': random.choice([True, False])
        })

    df_products = pd.DataFrame(products_data)
    df_products.to_sql('Dim_Products', engine, if_exists='append', index=False)
    print("Препарати завантажено.")

    df_prod_db = pd.read_sql("SELECT ProductID, BasePrice FROM Dim_Products", engine)

    start_date = datetime(2025, 1, 1)
    sales_data = []

    print("Генеруємо 10 000 транзакцій продажів (це займе кілька секунд)...")
    for _ in range(10000):
        random_days = random.randint(0, 364)
        sale_date = start_date + timedelta(days=random_days, hours=random.randint(8, 22))

        product = df_prod_db.sample(1).iloc[0]

        actual_price = round(product['BasePrice'] * random.uniform(0.9, 1.1), 2)

        sales_data.append({
            'ProductID': int(product['ProductID']),
            'PharmacyID': random.choice(pharm_ids),
            'SaleDate': sale_date,
            'Quantity': random.choices([1, 2, 3, 4, 5], weights=[70, 15, 10, 3, 2])[0],  # Чаще покупают по 1 шт.
            'ActualPrice': actual_price
        })

    df_sales = pd.DataFrame(sales_data)
    df_sales.to_sql('Fact_Sales', engine, if_exists='append', index=False, chunksize=1000)

    print("Готово! База даних успішно заповнена тестовими даними.")


if __name__ == "__main__":
    generate_data()