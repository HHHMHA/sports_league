import tablib
from django.core.files import File
from django.db import transaction

from .models import Game, Team
from .resources import GameResource


class GameService:
    @classmethod
    def create_game(cls, home_team_name: str, home_team_score: int, away_team_name: str, away_team_score: int) -> Game:
        with transaction.atomic():
            home_team = Team.objects.get(name=home_team_name)
            away_team = Team.objects.get(name=away_team_name)

            game = Game.objects.create(
                home_team=home_team,
                home_team_score=home_team_score,
                away_team=away_team,
                away_team_score=away_team_score,
            )
            cls.update_team_statistics(game)
            return game

    @classmethod
    def update_game(cls, game_id: int, home_team_score: int, away_team_score: int) -> Game:
        with transaction.atomic():
            game = Game.objects.get(pk=game_id)
            # We can consider update to be a delete operation followed by add for statistics
            # Might do extra operations but looks better than adding extra conditions
            cls.update_team_statistics(game, delete=True)
            game.home_team_score = home_team_score
            game.away_team_score = away_team_score
            game.save()
            cls.update_team_statistics(game)
            return game

    @classmethod
    def delete_game(cls, game_id: int):
        with transaction.atomic():
            game = Game.objects.get(pk=game_id)
            cls.update_team_statistics(game, delete=True)
            game.delete()

    @classmethod
    def update_team_statistics(cls, game, delete=False):
        home_team = game.home_team
        away_team = game.away_team

        if delete:
            home_team.games_count -= 1
            away_team.games_count -= 1
            if game.is_draw:
                home_team.draws -= 1
                away_team.draws -= 1
            elif game.is_winner(home_team):
                home_team.wins -= 1
                away_team.loses -= 1
            else:
                home_team.loses -= 1
                away_team.wins -= 1
        else:
            home_team.games_count += 1
            away_team.games_count += 1
            if game.is_draw:
                home_team.draws += 1
                away_team.draws += 1
            elif game.is_winner(home_team):
                home_team.wins += 1
                away_team.loses += 1
            else:
                home_team.loses += 1
                away_team.wins += 1

        home_team.save()
        away_team.save()

    @classmethod
    def import_games_from_csv(cls, file: File):
        try:
            dataset = tablib.Dataset().load(
                file.read().decode("utf-8"),
                format="csv",
                delimiter=",",
                headers=False,
            )
            dataset.headers = [
                "home_team",
                "home_team_score",
                "away_team",
                "away_team_score",
            ]
            dataset.insert_col(0, col=lambda x: "", header="id")
        except Exception:
            return False

        return cls.import_games(dataset)

    @classmethod
    def import_games(cls, dataset: tablib.Dataset):
        resource = GameResource()
        try:
            resource.import_data(dataset, dry_run=False, raise_errors=True)
            return True
        except Exception:
            return False
