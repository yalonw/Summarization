from django.urls import path, include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.homepage),
    path('analyze-result', views.summary_esbert, name='analyze_article'),
]