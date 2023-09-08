from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from sports_league.sports.models import Game, Team

from ..services import GameService
from ..strategy import Selector
from .serializers import GameSerializer


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        GameService.delete_game(instance.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeamViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=["GET"], url_name="ranks", url_path="ranks", detail=False)
    def ranks(self, request, *args, **kwargs):
        ranks = Team.ranks(request)
        for rank in ranks:
            rank["team"] = rank["team"].name
        return Response(data=ranks)

    @action(methods=["GET"], url_name="strategies", url_path="strategies", detail=False)
    def strategies(self, request, *args, **kwargs):
        strategies = Selector().strategies
        for data in strategies.values():
            data.pop("strategy_class")
        return Response(data=strategies)
