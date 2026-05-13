import pandas as pd
from sqlalchemy import create_engine

SERVER = 'localhost'
DATABASE = 'diploma'

CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
try:
    engine = create_engine(CONNECTION_STRING)
    print("Успешное подключение к MS SQL Server!")
except Exception as e:
    print("Ошибка подключения:", e)