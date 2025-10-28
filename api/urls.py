from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BotViewSet, ScenarioViewSet, StepViewSet

router = DefaultRouter()
router.register(r'bots', BotViewSet, basename='bot')
router.register(r'scenarios', ScenarioViewSet, basename='scenario')
router.register(r'steps', StepViewSet, basename='step')

urlpatterns = [
    path('', include(router.urls)),
]