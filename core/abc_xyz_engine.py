import pandas as pd
from sqlalchemy import create_engine
import numpy as np


class InventoryAnalyzer:
    def __init__(self, server, database):
        """Инициализация подключения к базе данных"""
        self.connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        self.engine = create_engine(self.connection_string)

    def fetch_data(self):
        """Выгрузка исторических данных о продажах из MS SQL Server"""
        query = """
                SELECT p.ProductID, \
                       p.ProductName, \
                       s.SaleDate, \
                       s.Quantity, \
                       (s.Quantity * s.ActualPrice) as TotalAmount
                FROM Fact_Sales s
                         JOIN Dim_Products p ON s.ProductID = p.ProductID \
                """
        print("Выгрузка данных из базы...")
        df = pd.read_sql(query, self.engine)
        # Преобразуем столбец с датой в правильный формат
        df['SaleDate'] = pd.to_datetime(df['SaleDate'])
        return df

    def calculate_abc(self, df):
        """Алгоритм АВС-анализа (по доходу)"""
        print("Расчет ABC-анализа...")
        # Группируем по товарам и считаем общую выручку
        abc_df = df.groupby(['ProductID', 'ProductName'])['TotalAmount'].sum().reset_index()

        # Сортируем по убыванию выручки
        abc_df = abc_df.sort_values(by='TotalAmount', ascending=False)

        # Считаем кумулятивную сумму и кумулятивный процент
        total_revenue = abc_df['TotalAmount'].sum()
        abc_df['CumSum'] = abc_df['TotalAmount'].cumsum()
        abc_df['CumPerc'] = (abc_df['CumSum'] / total_revenue) * 100

        # Функция для присвоения класса ABC
        def assign_abc(perc):
            if perc <= 80:
                return 'A'
            elif perc <= 95:
                return 'B'
            else:
                return 'C'

        abc_df['ABC_Class'] = abc_df['CumPerc'].apply(assign_abc)
        return abc_df[['ProductID', 'ProductName', 'TotalAmount', 'ABC_Class']]

    def calculate_xyz(self, df):
        """Алгоритм XYZ-анализа (по стабильности спроса)"""
        print("Расчет XYZ-анализа...")
        # Группируем продажи по месяцам для каждого товара
        df['MonthYear'] = df['SaleDate'].dt.to_period('M')
        monthly_sales = df.groupby(['ProductID', 'MonthYear'])['Quantity'].sum().reset_index()

        # Считаем среднее значение и стандартное отклонение для каждого товара
        xyz_df = monthly_sales.groupby('ProductID')['Quantity'].agg(['mean', 'std']).reset_index()

        # Заполняем NaN нулями (если товар продавался только 1 месяц, std рассчитать нельзя)
        xyz_df['std'] = xyz_df['std'].fillna(0)

        # Считаем коэффициент вариации (CV) в процентах
        # Избегаем деления на ноль
        xyz_df['CV'] = np.where(xyz_df['mean'] > 0, (xyz_df['std'] / xyz_df['mean']) * 100, 0)

        # Функция для присвоения класса XYZ
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
        """Главный метод, запускающий полный анализ и склеивающий результаты"""
        df = self.fetch_data()

        if df.empty:
            print("Нет данных для анализа!")
            return None

        abc_result = self.calculate_abc(df)
        xyz_result = self.calculate_xyz(df)

        # Склеиваем две таблицы по ProductID (Merge)
        matrix_df = pd.merge(abc_result, xyz_result, on='ProductID')

        # Создаем итоговую категорию (например, A + X = AX)
        matrix_df['Category_Matrix'] = matrix_df['ABC_Class'] + matrix_df['XYZ_Class']

        # Добавляем базовые рекомендации
        def get_recommendation(matrix):
            if matrix in ['AX', 'BX']:
                return 'Автоматический заказ (Reorder Point)'
            elif matrix in ['AY', 'BY']:
                return 'Создать страховой запас'
            elif matrix in ['AZ', 'BZ']:
                return 'Ручной контроль менеджером'
            elif matrix in ['CX', 'CY']:
                return 'Редкие заказы крупными партиями'
            elif matrix == 'CZ':
                return 'Кандидат на списание / Под заказ'
            return '-'

        matrix_df['Recommendation'] = matrix_df['Category_Matrix'].apply(get_recommendation)

        print("\nАнализ успешно завершен!")
        return matrix_df