import pytest

from ..models import Team
from ..services import GameService
from ..strategy import Default, Selector, WinsRatio


class TestSelector:
    def test_strategies(self):
        assert len(Selector().strategies) == 2

    def test_strategy__default(self):
        assert isinstance(Selector().strategy(), Default)

    def test_strategy__query_params(self, rf, user):
        request = rf.get("/test")
        request.user = user
        request.query_params = {"strategy": WinsRatio.code}
        assert isinstance(Selector().strategy(request), WinsRatio)

    def test_strategy__get(self, rf, user):
        request = rf.get("/test")
        request.user = user
        request.GET = {"strategy": WinsRatio.code}
        assert isinstance(Selector().strategy(request), WinsRatio)


@pytest.mark.django_db
class TestStrategies:
    def test_default(self):
        team_a = Team.objects.create(name="Team A")
        Team.objects.create(name="Team B")
        Team.objects.create(name="Team C")

        GameService.create_game("Team A", 3, "Team B", 2)
        GameService.create_game("Team A", 1, "Team B", 2)
        GameService.create_game("Team C", 3, "Team A", 3)

        team_a.refresh_from_db()
        assert Default().calculate_points(team_a) == 4

    def test_wins_ratio(self):
        team_a = Team.objects.create(name="Team A")
        Team.objects.create(name="Team B")
        Team.objects.create(name="Team C")

        GameService.create_game("Team A", 3, "Team B", 2)
        GameService.create_game("Team A", 3, "Team B", 2)
        GameService.create_game("Team C", 3, "Team A", 3)

        team_a.refresh_from_db()
        assert WinsRatio().calculate_points(team_a) == 1

    def test_wins_ratio__zero_error(self):
        team_a = Team.objects.create(name="Team A")
        assert WinsRatio().calculate_points(team_a) == 0
