from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from rest_framework.permissions import IsAuthenticated

from sports_league.common.permissions import PermissionClassesMixin

from .forms import ImportGamesForm
from .strategy import Selector


class GamesView(TemplateView):
    template_name = "sports/games.html"


class ImportGamesView(PermissionClassesMixin, FormView):
    permission_classes = [IsAuthenticated]
    template_name = "sports/import.html"
    form_class = ImportGamesForm
    success_url = reverse_lazy("sports:games")


class RankView(TemplateView):
    template_name = "sports/ranks.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["strategies"] = Selector().strategies
        return ctx
