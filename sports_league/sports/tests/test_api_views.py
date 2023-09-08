import pytest
from django.urls import reverse
from rest_framework import status

from sports_league.sports.models import Game, Team
from sports_league.sports.services import GameService


@pytest.mark.django_db
class TestGameViews:
    def test_list_games(self, api_auth_client):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = Game.objects.create(home_team=team1, home_team_score=2, away_team=team2, away_team_score=1)

        url = reverse("api:game-list")
        response = api_auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["id"] == game.id

    def test_create_game(self, api_auth_client):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")

        data = {
            "home_team": team1.id,
            "home_team_score": 2,
            "away_team": team2.id,
            "away_team_score": 1,
        }

        url = reverse("api:game-list")
        response = api_auth_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Game.objects.count() == 1

    @pytest.mark.django_db
    def test_update_game(self, api_auth_client):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game(team1.name, 2, team2.name, 5)

        data = {
            "home_team_score": 3,
            "away_team_score": 2,
        }

        url = reverse("api:game-detail", args=[game.pk])
        response = api_auth_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        game.refresh_from_db()
        assert game.home_team_score == 3
        assert game.away_team_score == 2

        assert game.home_team.wins == 1
        assert game.home_team.loses == 0
        assert game.home_team.draws == 0
        assert game.home_team.games_count == 1

        assert game.away_team.wins == 0
        assert game.away_team.loses == 1
        assert game.away_team.draws == 0
        assert game.away_team.games_count == 1

    @pytest.mark.django_db
    def test_update_game__cant_update_names(self, api_auth_client):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game(team1.name, 2, team2.name, 5)

        data = {
            "home_team": "Team C",
            "home_team_score": 3,
            "away_team": "Team D",
            "away_team_score": 2,
        }

        url = reverse("api:game-detail", args=[game.pk])
        response = api_auth_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        game.refresh_from_db()
        assert game.home_team_score == 3
        assert game.away_team_score == 2
        assert game.home_team.name == "Team A"
        assert game.away_team.name == "Team B"

    @pytest.mark.django_db
    def test_delete_game(self, api_auth_client):
        team1 = Team.objects.create(name="Team A")
        team2 = Team.objects.create(name="Team B")
        game = GameService.create_game(team1.name, 2, team2.name, 5)

        url = reverse("api:game-detail", args=[game.pk])
        response = api_auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Game.objects.count() == 0

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
