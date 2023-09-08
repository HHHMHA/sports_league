import pytest

from ..models import Game, Team


@pytest.mark.django_db
class TestTeam:
    def test_update_statistics(self):
        home_team = Team.objects.create(name="Team A")
        away_team = Team.objects.create(name="Team B")
        Game.objects.create(home_team=home_team, home_team_score=2, away_team=away_team, away_team_score=1)
        Game.objects.create(home_team=home_team, home_team_score=0, away_team=away_team, away_team_score=1)
        Game.objects.create(home_team=home_team, home_team_score=1, away_team=away_team, away_team_score=1)

        assert home_team.wins == 0
        assert home_team.loses == 0
        assert home_team.draws == 0
        assert home_team.games_count == 0

        home_team.update_statistics()

        assert home_team.wins == 1
        assert home_team.loses == 1
        assert home_team.draws == 1
        assert home_team.games_count == 3


@pytest.mark.django_db
class TestGame:
    def test_is_draw(self):
        home_team = Team.objects.create(name="Team A")
        away_team = Team.objects.create(name="Team B")
        game1 = Game.objects.create(home_team=home_team, home_team_score=2, away_team=away_team, away_team_score=2)
        game2 = Game.objects.create(home_team=home_team, home_team_score=0, away_team=away_team, away_team_score=1)

        assert game1.is_draw
        assert not game2.is_draw

    def test_is_winner(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game1 = Game.objects.create(home_team=team1, home_team_score=2, away_team=team2, away_team_score=1)
        game2 = Game.objects.create(home_team=team1, home_team_score=1, away_team=team2, away_team_score=2)

        assert game1.is_winner(team1)
        assert not game1.is_winner(team2)
        assert not game2.is_winner(team1)
        assert game2.is_winner(team2)

    def test_is_loser(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game1 = Game.objects.create(home_team=team1, home_team_score=2, away_team=team2, away_team_score=1)
        game2 = Game.objects.create(home_team=team1, home_team_score=1, away_team=team2, away_team_score=2)

        assert not game1.is_loser(team1)
        assert game1.is_loser(team2)
        assert game2.is_loser(team1)
        assert not game2.is_loser(team2)
