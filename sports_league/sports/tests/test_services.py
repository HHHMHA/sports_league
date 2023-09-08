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

    def test_import_games_from_csv(self, game_csv):
        result = GameService.import_games_from_csv(game_csv)

        assert result is True

        games = Game.objects.all()
        assert games.count() == 3

        # we can instead mock update_team_statistics and assert it was called since we already tested it
        team_a = Team.objects.get(name="Team A")
        team_b = Team.objects.get(name="Team B")
        team_c = Team.objects.get(name="Team C")

        assert team_a.wins == 1
        assert team_a.loses == 2
        assert team_a.draws == 0
        assert team_a.games_count == 3

        assert team_b.wins == 1
        assert team_b.loses == 1
        assert team_b.draws == 0
        assert team_b.games_count == 2

        assert team_c.wins == 1
        assert team_c.loses == 0
        assert team_c.draws == 0
        assert team_c.games_count == 1

    def test_import_games(self, game_dataset):
        result = GameService.import_games(game_dataset)

        assert result is True

        games = Game.objects.all()
        assert games.count() == 1

        game = games.first()
        assert game.home_team.name == "Team A"
        assert game.home_team_score == 2
        assert game.away_team.name == "Team B"
        assert game.away_team_score == 1

        # we can instead mock update_team_statistics and assert it was called since we already tested it
        assert game.home_team.wins == 1
        assert game.home_team.loses == 0
        assert game.home_team.draws == 0
        assert game.home_team.games_count == 1

        assert game.away_team.wins == 0
        assert game.away_team.loses == 1
        assert game.away_team.draws == 0
        assert game.away_team.games_count == 1
