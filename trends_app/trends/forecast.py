"""Модуль выполняет прогноз цен на основе ретроспективной динамики.
Учитывается горизонт прогноза, выбранный пользователем.
Из нескольких прогнозов на основе предшествующих временных рядов
разной длины выбирается вариант, имеющий наиболее высокий показатель R2.
"""

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold

import pandas as pd
import numpy as np


def linear_trend(data: pd.DataFrame, n_months: int) -> pd.DataFrame:
    """Функция выполняет прогноз цен с использованием модели
    линейной регрессии. Возвращает прогноз с оптимальным R2."""

    best_r2 = -1
    best_model = None
    best_period = None

    # Перебираем варианты временных рядов от 1/2 прогнозного периода до 4 прогнозных периодов:
    for prev_period in (n_months // 2 + 1, n_months, n_months * 2, n_months * 3, n_months * 4):
        X = np.array([i for i in range(prev_period * 30)]).reshape(-1, 1)
        y = data['price'].tail(prev_period * 30)

        model = LinearRegression()
        kf = KFold(5, shuffle=True)
        r2 = cross_val_score(model, X, y, cv=kf, scoring='r2').mean()

        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_period = prev_period

    # Прогноз на основе оптимальной модели:
    X = np.array([i for i in range(best_period * 30)]).reshape(-1, 1)
    y = data['price'].tail(best_period * 30)
    best_model.fit(X, y)

    trend_X = np.array([i for i in range(best_period * 30 + n_months * 30)]).reshape(-1, 1)
    trend_y = best_model.predict(trend_X)

    # Преобразуем полученный результат в датафрейм:
    # линия тренда включает предшествующий и прогнозный период с датами и ценами.
    start_day = data['date'].tail(best_period * 30).min()
    periods = (best_period + n_months) * 30
    trend_dates = pd.date_range(start=start_day, periods=periods, freq='D')
    forecast_df = pd.DataFrame({'date': trend_dates, 'price': trend_y})

    return forecast_df
