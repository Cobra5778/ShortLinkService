from django.db import models

# Create your models here.

class ShortLinks(models.Model):
    session_key = models.CharField(max_length=40, null=False, default='', db_index=True,
                                   verbose_name='Идентификатор сессии')
    urls = models.CharField(max_length=2048, verbose_name='Пользовательская ссылка')
    shortlink = models.CharField(max_length=15, unique=True, verbose_name='Короткая ссылка')
    crt_date = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    valid_days = models.IntegerField(default=14, verbose_name='Срок действия в днях')
    def __str__(self):
        return f"{self.shortlink} для \"{self.urls}\""

    def get_absolute_url(self):
        return '/%s/' % self.urls