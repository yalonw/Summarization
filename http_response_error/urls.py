from django.urls import path, include
from . import views

urlpatterns = [
    path('400', views.bad_request),
    path('403', views.forbidden),
    path('404', views.page_not_found),
    path('500', views.server_error),
    path('loading', views.loadingpage),
]