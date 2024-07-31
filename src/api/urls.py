from django.urls import path, include
from rest_framework import routers
from .views import TaskViewSet, UserViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register('tasks', TaskViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include(router.urls)),
]