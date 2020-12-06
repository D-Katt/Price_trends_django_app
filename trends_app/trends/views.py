from django.shortcuts import render, redirect
from trends.models import Price
from django.contrib.auth.models import User

from trends.forecast import linear_trend

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
        except Exception:
            # Если пользователь вводит ссылку на /trend/ не выбрав категорию,
            # перенаправляем его на главную страницу сайта:
            return redirect('/')

    # Извлекаем из базы данных нужные столбцы и преобразуем в pd.DataFrame:
    prices = Price
    data = pd.DataFrame(Price.objects.all().values('date', item))
    data.columns = ['date', 'price']

    # Делаем прогноз:
    forecast = linear_trend(data, n_months)

    # График для отображения на странице:
    fig_actual = Scatter(x=data['date'], y=data['price'],
                  mode='lines', name='Динамика',
                  opacity=0.8, marker_color='green')
    fig_trend = Scatter(x=forecast['date'], y=forecast['price'],
                  mode='lines', name='Прогноз',
                  opacity=0.8, marker_color='red')
    plot_div = plot([fig_actual, fig_trend], output_type='div')
 
    context = {
        'item': item_names[item],
        'plot_div': plot_div
    }

    return render(request, 'trends/trend.html', context=context)
