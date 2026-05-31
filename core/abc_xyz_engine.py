import pandas as pd
from sqlalchemy import create_engine
import numpy as np

class InventoryAnalyzer:
    def __init__(self, server, database):
        """Ініціалізація підключення до бази даних"""
        self.connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        self.engine = create_engine(self.connection_string)

    def fetch_data(self):
        """Вивантаження історичних даних про продажі з MS SQL Server"""
        query = """
                SELECT p.ProductID, \
                       p.ProductName, \
                       s.SaleDate, \
                       s.Quantity, \
                       (s.Quantity * s.ActualPrice) as TotalAmount
                FROM Fact_Sales s
                         JOIN Dim_Products p ON s.ProductID = p.ProductID \
                """
        print("Вивантаження даних з бази...")
        df = pd.read_sql(query, self.engine)
        df['SaleDate'] = pd.to_datetime(df['SaleDate'])
        return df

    def calculate_abc(self, df):
        """Алгоритм АВС-аналізу (за доходом)"""
        print("Розрахунок ABC-аналізу...")
        abc_df = df.groupby(['ProductID', 'ProductName'])['TotalAmount'].sum().reset_index()
        abc_df = abc_df.sort_values(by='TotalAmount', ascending=False)

        total_revenue = abc_df['TotalAmount'].sum()
        abc_df['CumSum'] = abc_df['TotalAmount'].cumsum()
        abc_df['CumPerc'] = (abc_df['CumSum'] / total_revenue) * 100

        def assign_abc(perc):
            if perc <= 80:
                return 'A'
            elif perc <= 95:
                return 'B'
            else:
                return 'C'

        abc_df['ABC_Class'] = abc_df['CumPerc'].apply(assign_abc)
        return abc_df[['ProductID', 'ProductName', 'TotalAmount', 'CumPerc', 'ABC_Class']]

    def calculate_xyz(self, df):
        """Алгоритм XYZ-аналізу (за стабільністю попиту)"""
        print("Розрахунок XYZ-аналізу...")
        df['MonthYear'] = df['SaleDate'].dt.to_period('M')
        monthly_sales = df.groupby(['ProductID', 'MonthYear'])['Quantity'].sum().reset_index()

        xyz_df = monthly_sales.groupby('ProductID')['Quantity'].agg(['mean', 'std']).reset_index()
        xyz_df['std'] = xyz_df['std'].fillna(0)

        xyz_df['CV'] = np.where(xyz_df['mean'] > 0, (xyz_df['std'] / xyz_df['mean']) * 100, 0)

        def assign_xyz(cv):
            if cv <= 10:
                return 'X'
            elif cv <= 25:
                return 'Y'
            else:
                return 'Z'

        xyz_df['XYZ_Class'] = xyz_df['CV'].apply(assign_xyz)
        return xyz_df[['ProductID', 'CV', 'XYZ_Class']]

    def run_matrix_analysis(self):
        """Головний метод, що запускає повний аналіз та об'єднує результати"""
        df = self.fetch_data()

        if df.empty:
            print("Немає даних для аналізу!")
            return None

        abc_result = self.calculate_abc(df)
        xyz_result = self.calculate_xyz(df)

        matrix_df = pd.merge(abc_result, xyz_result, on='ProductID')
        matrix_df['Category_Matrix'] = matrix_df['ABC_Class'] + matrix_df['XYZ_Class']

        def get_recommendation(matrix):
            if matrix in ['AX', 'BX']:
                return 'Автоматичне замовлення (Reorder Point)'
            elif matrix in ['AY', 'BY']:
                return 'Створити страховий запас'
            elif matrix in ['AZ', 'BZ']:
                return 'Ручний контроль менеджером'
            elif matrix in ['CX', 'CY']:
                return 'Рідкісні замовлення великими партіями'
            elif matrix == 'CZ':
                return 'Кандидат на списання / Під замовлення'
            return '-'

        matrix_df['Recommendation'] = matrix_df['Category_Matrix'].apply(get_recommendation)

        print("\nАналіз успішно завершено!")
        return matrix_df