from django.db import models
from django.utils.functional import cached_property
from django_extensions.db.models import TimeStampedModel

from sports_league.sports.strategy import Selector


class Team(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    # These properties exist to make things faster when raking and will be set by game services functions
    # games should only be added using their services to ensure integrity
    wins = models.PositiveIntegerField(default=0, editable=False)
    loses = models.PositiveIntegerField(default=0, editable=False)
    draws = models.PositiveIntegerField(default=0, editable=False)
    games_count = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return self.name if self.name else ""

    def update_statistics(self):
        """This is used just in case anything happened and the above fields became incorrect"""

        games = self.games

        self.games_count = games.count()
        self.wins = 0
        self.loses = 0
        self.draws = 0

        for game in games:
            if game.is_draw:
                self.draws += 1
            elif game.is_winner(self):
                self.wins += 1
            else:
                self.loses += 1

        self.save()

    update_statistics.alters_data = True

    @cached_property
    def games(self):
        return self.home_games.all() | self.away_games.all()

    def points(self, request=None):
        return Selector().strategy(request=request).calculate_points(self)

    @classmethod
    def ranks(cls, request=None):
        result = [{"team": team, "points": team.points(request)} for team in cls.objects.all()]
        result.sort(key=lambda team_dict: (-team_dict["points"], team_dict["team"].name))

        rank = 0
        previous_points = None
        for team_dict in result:
            if team_dict["points"] != previous_points:
                rank += 1
            team_dict["rank"] = rank
            previous_points = team_dict["points"]

        return result


class Game(TimeStampedModel):
    home_team = models.ForeignKey(Team, related_name="home_games", on_delete=models.CASCADE)
    home_team_score = models.PositiveIntegerField()
    away_team = models.ForeignKey(Team, related_name="away_games", on_delete=models.CASCADE)
    away_team_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.home_team} with {self.home_team_score}--{self.away_team} with {self.away_team_score}"

    @property
    def is_draw(self):
        return self.away_team_score == self.home_team_score

    def is_winner(self, team):
        return self.winner_team == team

    def is_loser(self, team):
        return self.loser_team == team

    @property
    def winner_team(self):
        if self.is_draw:
            return None

        if self.home_team_score > self.away_team_score:
            return self.home_team

        return self.away_team

    @property
    def loser_team(self):
        if self.is_draw:
            return None

        if self.home_team_score > self.away_team_score:
            return self.away_team

        return self.home_team
