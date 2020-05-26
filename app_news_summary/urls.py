from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.homepage),
    path('news-summary', views.homepage),    
    path('news-summary-search', views.summary_1, name='search_keyword'),
    # path('news-summary-search/<str:keyword>', views.summary_1, name='search_keyword'),
    # path('wordcloud', views.wc_1),
    path('test', views.search_page_test),
]