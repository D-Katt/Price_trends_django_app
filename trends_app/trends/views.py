from django.shortcuts import render, redirect
from trends.models import Price
from django.contrib.auth.models import User

from trends.forecast import get_forecast

from plotly.offline import plot
from plotly.graph_objs import Scatter

import pandas as pd

# Словарь для преобразования названий столбцов базы данных в названия для заголовка над графиком:
item_names = {'gold_price': 'золото', 'oil_price': 'нефть', 'copper_price': 'медь'}


def home_page(request):
    """Функция отображает главную страницу сайта."""
    return render(request, 'trends/home.html')


def trend(request):
    """Функция отображает страницу с динамикой и прогнозом цен
    выбранного товара / категории."""

    # Извлекаем из запроса наименование товара:
    if request.method == 'GET':
        try:
            item = request.GET['items']
            n_months = int(request.GET['months'])
            method = request.GET['methods']
        except Exception:
            # Если пользователь вводит ссылку на /trend/ не выбрав категорию,
            # перенаправляем его на главную страницу сайта:
            return redirect('/')

    # Извлекаем из базы данных нужные столбцы и преобразуем в pd.DataFrame:
    prices = Price
    data = pd.DataFrame(Price.objects.all().values('date', item))
    data.columns = ['date', 'price']

    # Делаем прогноз:
    forecast = get_forecast(data, n_months, method)

    # График с фактическими значениями и прогнозом:
    plot_div = plot_data(data, forecast)

    # Таблица с ежемесячным прогнозом:
    table_div, pred_price, pc_change = create_table(forecast, n_months)

    context = {
        'item': item_names[item],
        'plot_div': plot_div,
        'table_div': table_div,
        'pred_price': pred_price,
        'pc_change': pc_change
    }

    return render(request, 'trends/trend.html', context=context)


def plot_data(original_data: pd.DataFrame, forecast_data: pd.DataFrame):
    """Функция формирует интерактивный график с динамикой цен и прогнозом
    для отображения на html-странице."""

    fig_actual = Scatter(x=original_data['date'], y=original_data['price'],
                  mode='lines', name='Динамика',
                  opacity=0.8, marker_color='green')

    # Если получен корректный прогноз, отображаем его на графике с предшествующей динамикой.
    if forecast_data['price'].isna().sum() == 0:
        fig_trend = Scatter(x=forecast_data['date'], y=forecast_data['price'],
                            mode='lines', name='Прогноз',
                            opacity=0.8, marker_color='red')

        plot_div = plot([fig_actual, fig_trend], output_type='div')
    
    # Если в прогнозе есть значения np.nan, показываем только динамику фактических данных.
    else:
        plot_div = plot([fig_actual], output_type='div')

    return plot_div


def create_table(forecast_data: pd.DataFrame, n_months: int):
    """Функция формирует и возвращает элемент <table> с ежемесячным прогнозом цен
    для отображения на html-странице, стоимость на конец прогнозного периода
    и изменение по сравнению с последними фактическими данными в процентах."""

    # Проверяем, что получен корректный прогноз
    # (на некоторых временных отрезках экпоненциальное сглаживание
    # приводит к ошибке: Optimization failed to converge и значениям np.nan).
    if forecast_data['price'].isna().sum() == 0:

        # Индексы строк в прогнозном датафрейме с шагом в 30 дней:
        n_periods = len(forecast_data) // 30
        monthly_indexes = [i * 30 - 1 for i in range(n_periods - n_months, n_periods + 1)]
    
        # Выбираем строки прогноза с шагом в 30 дней:
        monthly_forecast = forecast_data.iloc[monthly_indexes, :].copy()
        monthly_forecast['date'] = monthly_forecast['date'].apply(lambda x: x.date)
        
        # Цена на конец прогнозного периода и изменение в процентах к последним фактическим данным:
        last_actual_price = monthly_forecast.iloc[0, :]['price']
        last_forecasted_price = round(monthly_forecast.iloc[len(monthly_forecast) - 1, :]['price'], 2)
        pc_change = str(round((last_forecasted_price / last_actual_price - 1) * 100, 2)) + '%'

        # Создаем элемент html:
        monthly_forecast.columns = ['Дата', 'Цена']
        table = monthly_forecast.iloc[1:, :].to_html(index=False, 
                                                    float_format='{:10.2f}'.format, 
                                                    classes=['table', 'table-striped'], 
                                                    justify='center')
    
    # Если из модели экспоненциального сглаживания получены значения np.nan,
    # вместо прогнозных значений отображаем для пользователя сообщение об ошибке.
    else:
        table = ''
        last_forecasted_price = 'нет данных'
        pc_change = 'не удалось выполнить прогноз для выбранного периода, выберите другой метод или измените горизонт прогноза'

    return table, last_forecasted_price, pc_change
