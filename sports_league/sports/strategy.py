# Inspired by django oscar strategy for pricing
import copy

from django.utils.translation import gettext_lazy as _


class Selector:
    """
    Responsible for returning the appropriate strategy class for a given
    user/session.

    The request can be used to fetch a strategy based on a given query param
    user can have a preferred strategy

    """

    @property
    def strategies(self) -> dict:
        return copy.deepcopy(Base.strategies)

    def strategy(self, request=None, user=None, **kwargs) -> "Base":
        """
        Return an instantiated strategy instance
        """
        strategy_class = Default
        if request and hasattr(request, "query_params") and request.query_params.get("strategy") in self.strategies:
            strategy_class = self.strategies[request.query_params["strategy"]]["strategy_class"]
        if request and hasattr(request, "GET") and request.GET.get("strategy") in self.strategies:
            strategy_class = self.strategies[request.GET.get("strategy")]["strategy_class"]
        return strategy_class(request, user, **kwargs)


class BaseMeta(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, "strategies"):
            cls.strategies = {}
        else:
            cls.strategies[cls.code] = {
                "name": cls.display_name,
                "strategy_class": cls,
            }

        super().__init__(name, bases, attrs)


class Base(metaclass=BaseMeta):
    """
    The base strategy class

    Given a team, strategies are responsible for returning a
    ``points`` for that team:
    """

    display_name = None
    code = None

    def __init__(self, request=None, user=None, **kwargs):
        self.request = request
        self.user = user
        if request and request.user.is_authenticated and not user:
            self.user = request.user

    def calculate_points(self, team) -> int:
        """
        Given a team, return the team points.
        """
        raise NotImplementedError("A strategy class must define a rank_team method")


class Default(Base):
    display_name = _("Default")
    code = "default"

    def calculate_points(self, team) -> int:
        return team.wins * 3 + team.draws * 1 + team.loses * 0


class WinsRatio(Base):
    display_name = _("Wins/Games Ration")
    code = "wins_ratio"

    def calculate_points(self, team) -> int:
        if team.games_count == 0:
            return 0
        return int(round(team.wins / team.games_count))
