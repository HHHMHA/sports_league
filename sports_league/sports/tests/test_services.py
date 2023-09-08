import pytest

from ..models import Game, Team
from ..services import GameService


@pytest.mark.django_db
class TestGameService:
    def test_create_game(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")

        game = GameService.create_game("Team A", 2, "Team B", 1)
        assert game.home_team == team1
        assert game.home_team_score == 2
        assert game.away_team == team2
        assert game.away_team_score == 1

        team1.refresh_from_db()
        team2.refresh_from_db()
        assert team1.wins == 1
        assert team1.loses == 0
        assert team1.draws == 0
        assert team1.games_count == 1
        assert team2.wins == 0
        assert team2.loses == 1
        assert team2.draws == 0
        assert team2.games_count == 1

    def test_update_game(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game("Team A", 2, "Team B", 1)

        updated_game = GameService.update_game(game.id, 3, 2)

        assert updated_game.home_team_score == 3
        assert updated_game.away_team_score == 2

        team1.refresh_from_db()
        team2.refresh_from_db()
        assert team1.wins == 1
        assert team1.loses == 0
        assert team1.draws == 0
        assert team1.games_count == 1
        assert team2.wins == 0
        assert team2.loses == 1
        assert team2.draws == 0
        assert team2.games_count == 1

    def test_delete_game(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game("Team A", 2, "Team B", 1)

        GameService.delete_game(game.id)

        with pytest.raises(Game.DoesNotExist):
            game.refresh_from_db()

        team1.refresh_from_db()
        team2.refresh_from_db()
        assert team1.wins == 0
        assert team1.loses == 0
        assert team1.draws == 0
        assert team1.games_count == 0
        assert team2.wins == 0
        assert team2.loses == 0
        assert team2.draws == 0
        assert team2.games_count == 0

    def test_update_team_statistics__with_create_game(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")

        game = Game.objects.create(home_team=team1, home_team_score=2, away_team=team2, away_team_score=1)
        GameService.update_team_statistics(game)

        team1.refresh_from_db()
        team2.refresh_from_db()
        assert team1.wins == 1
        assert team1.loses == 0
        assert team1.draws == 0
        assert team1.games_count == 1
        assert team2.wins == 0
        assert team2.loses == 1
        assert team2.draws == 0
        assert team2.games_count == 1

    def test_update_team_statistics__delete_game(self):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game("Team A", 2, "Team B", 1)
        game.delete()

        GameService.update_team_statistics(game, delete=True)

        team1.refresh_from_db()
        team2.refresh_from_db()
        assert team1.wins == 0
        assert team1.loses == 0
        assert team1.draws == 0
        assert team1.games_count == 0
        assert team2.wins == 0
        assert team2.loses == 0
        assert team2.draws == 0
        assert team2.games_count == 0
