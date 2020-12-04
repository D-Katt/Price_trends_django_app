from django.urls import path
from . import views as trend_views

urlpatterns = [
    path('', trend_views.home_page, name='home'),  # Home page for login and item selection
    path('trend/', trend_views.trend, name='trend')  # Trend and forecast for selected item
]
