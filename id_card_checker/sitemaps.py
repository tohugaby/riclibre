"""
Id Card checker apps : Sitemaps module
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class IdCardclassStaticViewSitemap(Sitemap):
    """
    id_card view sitemap
    """
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return ['idcard']

    def location(self, obj):
        return reverse(obj)
