from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from sports_league.sports.apis.views import GameViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

app_name = "api"

router.register("", GameViewSet, basename="game")

urlpatterns = router.urls
