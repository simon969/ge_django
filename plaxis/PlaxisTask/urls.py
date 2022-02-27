from django.urls import include, path
from plaxis.PlaxisTask.views import PlaxisViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'PlaxisTask', PlaxisViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     # path('PlaxisTask/', views.plaxis_list),
#     path('PlaxisTask/download/<uuid:pk>/', views.PlaxisViewSet.download),
#     path('PlaxisTask/download/<uuid:pk>/<int:offset>/', views.PlaxisViewSet.download),
#     path('PlaxisTask/download/<uuid:pk>/<str:element>/', views.PlaxisViewSet.download),
#     path('PlaxisTask/start/<uuid:pk>/', views.PlaxisViewSet.start_task),
#     # path('PlaxisTask/AddNew', views.plaxis_add)
#     path('PlaxisTask/<int:pk>/download/<str:element>/', views.PlaxisViewSet.as_view({"get": "download"}))
#    ]
urlpatterns = [
    path('PlaxisTask/<uuid:pk>/download/<element>/', PlaxisViewSet.as_view({"get": "download"})),
]