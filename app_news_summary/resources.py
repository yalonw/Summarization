from import_export import resources
from .models import CrawlNews

class SummaryCrawlResource(resources.ModelResource):
    class Meta:
        model = SummaryCrawl

class CrawlNewsResource(resources.ModelResource):
    class Meta:
        model = CrawlNews