from django.db import models


class Price(models.Model):
    """Класс для хранения информации по динамике цен на товары."""
    
    date = models.DateTimeField(unique_for_date=True, null=False, editable=False, verbose_name='Date')

    oil_price = models.FloatField(null=True, editable=False, verbose_name='Brent')
    gold_price = models.FloatField(null=True, editable=False, verbose_name='Gold')
    copper_price = models.FloatField(null=True, editable=False, verbose_name='Copper')
