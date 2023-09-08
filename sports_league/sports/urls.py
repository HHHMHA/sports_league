from django.urls import path

from .views import GamesView, ImportGamesView, RankView

app_name = "sports"

urlpatterns = [
    path("import/", ImportGamesView.as_view(), name="import_games"),
    path("games/", GamesView.as_view(), name="games"),
    path("ranks/", RankView.as_view(), name="ranks"),
]
