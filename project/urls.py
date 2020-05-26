"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.views.generic import RedirectView
from http_response_error import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_news_summary.urls')),
    path('index/', RedirectView.as_view(url='/')),
    path('text-summary/', include('app_text_summary.urls')),
    path('error/', include('http_response_error.urls')),
    # path('redirect/', redirect),    
]

handler400 = 'http_response_error.views.bad_request'
handler403 = 'http_response_error.views.forbidden'
handler404 = 'http_response_error.views.page_not_found'
handler500 = 'http_response_error.views.server_error'
