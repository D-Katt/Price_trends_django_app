"""Модуль для преобразования исходных данных в формат json."""

import pandas as pd

# Считываем данные из текстовых файлов с разделителями:
oil_data = pd.read_csv('Brent.txt',
                       usecols=['<DATE>', '<CLOSE>'],
                       parse_dates=['<DATE>'],
                       index_col='<DATE>')
gold_data = pd.read_csv('Gold.txt',
                        usecols=['<DATE>', '<CLOSE>'],
                        parse_dates=['<DATE>'],
                        index_col='<DATE>')
copper_data = pd.read_csv('Copper.txt',
                          usecols=['<DATE>', '<CLOSE>'],
                          parse_dates=['<DATE>'],
                          index_col='<DATE>')

# Переименовываем одинаковые столбцы перед объединением:
oil_data.columns = ['oil_price']
gold_data.columns = ['gold_price']
copper_data.columns = ['copper_price']

# Объединяем данные по датам:
data = pd.concat([oil_data, gold_data, copper_data], axis='columns').reset_index()
data = data.rename({'<DATE>': 'date'}, axis='columns')

# Преобразуем в формат json:
data.to_json(path_or_buf='data.json', orient='records', date_format='iso')
