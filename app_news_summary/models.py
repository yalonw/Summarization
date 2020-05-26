from django.db import models

class summary_crawl(models.Model):
    title    = models.CharField(max_length=50)
    content  = models.TextField()
    time     = models.DateTimeField()
    url      = models.URLField()
    topic    = models.CharField(max_length=10)
    jeiba    = models.TextField()
    summary1 = models.TextField()