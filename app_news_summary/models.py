from django.db import models

class SummaryCrawl(models.Model):
	title = models.CharField(max_length=50)
	content = models.TextField()
	date = models.DateField()
	url = models.URLField()
	topic = models.CharField(max_length=10)
	jeiba = models.TextField()
	summary1 = models.TextField()

class CrawlNews(models.Model):
	title = models.CharField(max_length=100)
	sub_title = models.CharField(max_length=100,blank=True)
	content = models.TextField()
	sub_content = models.TextField(blank=True)
	date = models.DateField(blank=True)
	url = models.URLField()
