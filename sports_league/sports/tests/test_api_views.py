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


@pytest.mark.django_db
class TestTeamViews:
    def test_ranks(self, api_client):
        team1 = Team.objects.create(name="Team C")
        team1.wins = 3
        team1.loses = 2
        team1.draws = 1
        team1.games_count = 1
        team1.save()

        team2 = Team.objects.create(name="Team B")
        team2.wins = 1
        team2.loses = 2
        team2.draws = 3
        team2.games_count = 1
        team2.save()

        team3 = Team.objects.create(name="Team A")
        team3.wins = 3
        team3.loses = 2
        team3.draws = 1
        team3.games_count = 1
        team3.save()

        url = reverse("api:team-ranks")
        response = api_client.get(url)
        assert response.data == [
            {"points": 10, "team": "Team A", "rank": 1},
            {"points": 10, "team": "Team C", "rank": 1},
            {"points": 6, "team": "Team B", "rank": 2},
        ]

    def test_strategies(self, api_client):
        url = reverse("api:team-strategies")
        response = api_client.get(url)
        assert response.data == {"default": {"name": "Default"}, "wins_ratio": {"name": "Wins/Games Ration"}}
