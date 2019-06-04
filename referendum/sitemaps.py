"""
Referendum apps : Sitemaps module
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from referendum.models import Referendum


class IndexAndReferendumSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['index', 'referendum_list', 'my_referendums']

    def location(self, item):
        return reverse(item)


class ReferendumStaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return ['referendum_create', 'legal']

    def location(self, item):
        return reverse(item)


class ReferendumSitemap(Sitemap):
    """
    Referendum sitemap
    """
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        Referendum.objects.filter(publication_date__isnull=False)
