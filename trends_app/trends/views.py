from django.shortcuts import render
from trends.models import Price
from plotly.offline import plot
from plotly.graph_objs import Scatter

import pandas as pd

item_names = {'gold_price': 'золото', 'oil_price': 'нефть', 'copper_price': 'медь'}


def home_page(request):
    """Функция отображает главную страницу сайта."""
    return render(request, 'trends/home.html')


def trend(request):
    """Функция отображает страницу с динамикой и прогнозом цен
    выбранного товара / категории."""

    # TODO: Как-то передать имя столбца в запросе при переходе по ссылке
    item = 'copper_price'

    # Извлекаем из базы данных нужные столбцы и преобразуем в pd.DataFrame:
    prices = Price
    data = pd.DataFrame(Price.objects.all().values('date', item))

    # График для отображения на странице:
    x_data = data['date']
    y_data = data[item]
    fig = Scatter(x=x_data, y=y_data,
                  mode='lines', name='test',
                  opacity=0.8, marker_color='green')
    plot_div = plot([fig], output_type='div')
 
    context = {
        'item': item_names[item],
        'plot_div': plot_div
    }

    return render(request, 'trends/trend.html', context=context)
