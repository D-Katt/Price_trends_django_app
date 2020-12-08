"""Модуль выполняет прогноз цен на основе ретроспективной динамики.
Учитывается горизонт прогноза и метод, выбранный пользователем.
"""

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

from statsmodels.tsa.api import ExponentialSmoothing

import pandas as pd
import numpy as np


def get_forecast(data: pd.DataFrame, n_months: int, method: str) -> pd.DataFrame:
    """Функция выполняет прогноз цен с применением выбранного метода."""

    if method == 'linregression':
        forecast = linear_trend(data, n_months)
    elif method == 'expsmoothing':
        forecast = exponential_smoothing(data, n_months)

    return forecast


def linear_trend(data: pd.DataFrame, n_months: int) -> pd.DataFrame:
    """Функция выполняет прогноз цен с использованием модели
    линейной регрессии. Возвращает прогноз с оптимальным показателем R2."""

    best_r2 = -1
    best_period = None

    # Перебираем варианты временных рядов от 1/2 прогнозного периода до 4 прогнозных периодов:
    n_days = n_months * 30
    for prev_period in (n_days // 2, n_days, n_days * 2, n_days * 3, n_days * 4):
        X = np.array([i for i in range(prev_period)]).reshape(-1, 1)
        y = data['price'].tail(prev_period)

        model = LinearRegression()
        kf = KFold(5, shuffle=True)
        r2 = cross_val_score(model, X, y, cv=kf, scoring='r2').mean()

        if r2 > best_r2:
            best_r2, best_period = r2, prev_period

    # Прогноз на основе оптимального временного ряда для обучения модели:
    X = np.array([i for i in range(best_period)]).reshape(-1, 1)
    y = data['price'].tail(best_period)
    model = LinearRegression().fit(X, y)

    trend_X = np.array([i for i in range(best_period + n_days)]).reshape(-1, 1)
    trend_y = model.predict(trend_X)

    # Преобразуем полученный результат в датафрейм:
    # линия тренда включает предшествующий и прогнозный период с датами и ценами.
    forecast_df = pd.DataFrame({'date': data['date'].tail(best_period)})
    next_day = forecast_df['date'].max() + pd.to_timedelta('1 days')
    periods = n_days
    future_dates = pd.date_range(start=next_day, periods=periods, freq='D')
    forecast_df = forecast_df.append(pd.DataFrame({'date': future_dates}))
    forecast_df['price'] = trend_y

    return forecast_df


def exponential_smoothing(data: pd.DataFrame, n_months: int):
    """Функция выполняет прогноз цен с использованием
    модели экспоненциального сглаживания."""

    # Используем для обучения модели период, равный двум прогнозным периодам:
    prev_days = n_months * 30 * 2
    model = ExponentialSmoothing(data['price'].tail(prev_days), trend='add').fit()
    forecast = model.forecast(n_months * 30)

    # Преобразуем полученный прогноз в датафрейм и включаем
    # model.fittedvalues и будущий период с датами и ценами.
    forecast_df = pd.DataFrame({'date': data['date'].tail(prev_days), 'price': model.fittedvalues})    

    next_day = forecast_df['date'].max() + pd.to_timedelta('1 days')
    periods = n_months * 30
    future_dates = pd.date_range(start=next_day, periods=periods, freq='D')

    forecast_df = forecast_df.append(pd.DataFrame({'date': future_dates, 'price': forecast}))

    return forecast_df
