"""ge_py URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from ge_py.quickstart import views
from plaxis.PlaxisTask import urls as plaxis_urls, views as plaxis_views
from ags.AGSTask import urls as ags_urls, views as ags_views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'PlaxisTask', plaxis_views.PlaxisViewSet)
router.register(r'AGSTask', ags_views.AGSTaskViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(plaxis_urls.urlpatterns)),
    path('', include(ags_urls.urlpatterns))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


