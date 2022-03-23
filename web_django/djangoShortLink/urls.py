"""djangoShortLink URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
#from shortlink.views import redirectsubpath, mainapp, check_custom_subpart
from shortlink.views import mainform, urls_table, redirect_to_url
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainform, name='mainform'),
    path('urls/', urls_table, name='urls_table'),
    #path('(?P<short_url>[-\w]+)$/', redirect_to_url, name='redirect_to_url'),
    path('<path:short_url>/', redirect_to_url, name='redirect_to_url'),

]

handler404 = "shortlink.views.page_not_found_view"
handler500 = "shortlink.views.server_error"
handler301 = "shortlink.views.many_redirects"