from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status

from sports_league.sports.services import GameService


@pytest.mark.django_db
class TestGameViews:
    def test_import_games_view(self, auth_client, game_csv):
        with patch.object(GameService, "import_games_from_csv") as mock:
            csv_file = SimpleUploadedFile("logo.png", game_csv.read(), content_type="text/csv")
            url = reverse("sports:import_games")
            data = {
                "file": csv_file,
            }
            response = auth_client.post(url, data)
            assert status.is_redirect(response.status_code)
            mock.assert_called_once()


@pytest.mark.django_db
class TestTeamViews:
    def test_ranks_view(self, client, game_csv):
        url = reverse("sports:ranks")
        response = client.get(url)
        assert status.is_success(response.status_code)
