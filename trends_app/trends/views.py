from django.shortcuts import render


def home_page(request):
    """Функция отображает главную страницу сайта."""
    return render(request, 'trends/home.html')


def trend(request):
    """Функция отображает страницу с динамикой и прогнозом цен
    выбранного товара / категории."""
    return render(request, 'trends/trend.html')
