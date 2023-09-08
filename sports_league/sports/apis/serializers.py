from rest_framework import serializers
from rest_framework.fields import empty

from sports_league.common.api.fields import UniqueRelatedField
from sports_league.sports.models import Game, Team
from sports_league.sports.services import GameService


class GameSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

        if self.instance:
            # We don't want to update these fields
            self.fields["home_team"].read_only = True
            self.fields["away_team"].read_only = True

    home_team = UniqueRelatedField(
        unique_field="name",
        queryset=Team.objects.all(),
        create=True,
    )
    away_team = UniqueRelatedField(
        unique_field="name",
        queryset=Team.objects.all(),
        create=True,
    )

    class Meta:
        model = Game
        fields = (
            "id",
            "home_team",
            "home_team_score",
            "away_team",
            "away_team_score",
        )

    def create(self, validated_data):
        home_team = validated_data.pop("home_team")
        home_team_score = validated_data.pop("home_team_score")
        away_team = validated_data.pop("away_team")
        away_team_score = validated_data.pop("away_team_score")

        return GameService.create_game(home_team.name, home_team_score, away_team.name, away_team_score)

    def update(self, instance, validated_data):
        home_team_score = validated_data.pop("home_team_score")
        away_team_score = validated_data.pop("away_team_score")

        return GameService.update_game(instance.pk, home_team_score, away_team_score)
