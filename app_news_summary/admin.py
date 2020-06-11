from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


# Register your models here.
@admin.register(SummaryCrawl)
class SummaryCrawlAdmin(ImportExportModelAdmin):
	# 加入 ModelAdmin 類別，定義顯示欄位、欄位過濾資料、搜尋和排序
	list_display=('id','title','content','date','url','topic','jeiba','summary1')
	list_filter=('date','topic')
	serch_fields=('title',)
	ordering=('id',)

@admin.register(CrawlNews)
class CrawlNewsAdmin(ImportExportModelAdmin):
	list_display=('id','title','sub_title','content','sub_content','date','url')
	list_filter=('date',)
	serch_fields=('title',)
	ordering=('id',)
