"""riclibre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from id_card_checker.sitemaps import IdCardclassStaticViewSitemap
from referendum.models import Referendum
from referendum.sitemaps import ReferendumStaticViewSitemap, IndexAndReferendumSitemap

sitemaps = {
    'index_and_referendum': IndexAndReferendumSitemap,
    'static': ReferendumStaticViewSitemap,
    'id_cards': IdCardclassStaticViewSitemap,
    'referendum': GenericSitemap({
        'queryset': Referendum.objects.filter(publication_date__isnull=False),
        'date_field': 'last_update'
    })

}

urlpatterns = [
    path('', include('referendum.urls')),
    path('', include('id_card_checker.urls')),
    path('', include('achievements.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
