from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.homepage),
    path('news-summary/', views.homepage),    
    path('news-summary/search-result', views.summary_esjieba_crawl, name='search_keyword'),
    # path('wordcloud', views.wc_1),
]