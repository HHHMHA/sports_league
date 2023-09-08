from import_export import fields, resources, widgets

from .models import Game, Team


class GameResource(resources.ModelResource):
    home_team = fields.Field(
        attribute="home_team",
        widget=widgets.ForeignKeyWidget(Team, "name"),
    )
    away_team = fields.Field(
        attribute="away_team",
        widget=widgets.ForeignKeyWidget(Team, "name"),
    )

    class Meta:
        model = Game
        fields = ("id", "home_team", "home_team_score", "away_team", "away_team_score")

    def before_import_row(self, row, **kwargs):
        Team.objects.get_or_create(name=row["home_team"])
        Team.objects.get_or_create(name=row["away_team"])

    def after_save_instance(self, instance: Game, using_transactions, dry_run):
        if not using_transactions and dry_run:
            return None
        from sports_league.sports.services import GameService

        GameService.update_team_statistics(instance)
