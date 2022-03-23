from django.contrib import admin
from .models import ShortLinks

# Register your models here.

class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key', 'urls', 'shortlink', 'crt_date', 'valid_days')
    list_display_links = ('id', 'urls')
    search_fields = ('id', 'session_key', 'urls', 'shortlink')
    list_editable = ('valid_days',)
    list_filter = ('urls',)

admin.site.register(ShortLinks, ShortLinkAdmin)