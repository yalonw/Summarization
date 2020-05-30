from import_export import resources
from .models import CrawlNews

class CrawlNewsResource(resources.ModelResource):
    class Meta:
        model = CrawlNews