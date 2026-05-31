from sqlalchemy import create_engine

SERVER = 'localhost'
DATABASE = 'diploma'
CONNECTION_STRING = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

def get_engine():
    return create_engine(CONNECTION_STRING)