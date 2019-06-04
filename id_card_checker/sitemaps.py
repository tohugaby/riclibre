"""
Referendum apps : Sitemaps module
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from id_card_checker.models import IdCard


class IdCardclassStaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'never'

    def items(self):
        return ['idcard']

    def location(self, item):
        return reverse(item)
