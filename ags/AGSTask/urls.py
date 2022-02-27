from django.urls import include, path
from ags.AGSTask import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'AGSTask', views.AGSTaskViewSet)

urlpatterns = [
    path('AGSTask/<uuid:pk>/download/<element>/', views.AGSTaskViewSet.as_view({"get": "download"})),
   ]