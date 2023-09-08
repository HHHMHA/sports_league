from django.urls import path

from .views import GamesView, ImportGamesView

app_name = "sports"

urlpatterns = [
    path("import/", ImportGamesView.as_view(), name="import_games"),
    path("games/", GamesView.as_view(), name="games"),
]
