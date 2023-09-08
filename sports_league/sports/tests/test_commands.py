import pytest
from django.core.management import call_command

from ..models import Game, Team


@pytest.mark.django_db
class TestCommands:
    def test_update_teams_statistics(self):
        home_team = Team.objects.create(name="Team A")
        away_team = Team.objects.create(name="Team B")
        Game.objects.create(home_team=home_team, home_team_score=2, away_team=away_team, away_team_score=1)
        Game.objects.create(home_team=home_team, home_team_score=2, away_team=away_team, away_team_score=1)
        Game.objects.create(home_team=home_team, home_team_score=0, away_team=away_team, away_team_score=1)
        Game.objects.create(home_team=home_team, home_team_score=1, away_team=away_team, away_team_score=1)

        assert home_team.wins == 0
        assert home_team.loses == 0
        assert home_team.draws == 0
        assert home_team.games_count == 0

        call_command("update_teams_statistics")

        home_team.refresh_from_db()
        away_team.refresh_from_db()

        assert home_team.wins == 2
        assert home_team.loses == 1
        assert home_team.draws == 1
        assert home_team.games_count == 4

        assert away_team.wins == 1
        assert away_team.loses == 2
        assert away_team.draws == 1
        assert away_team.games_count == 4
