from django.core.management.base import BaseCommand
from django.utils import timezone

from sports_league.sports.models import Team


class Command(BaseCommand):
    help = "Update Team Statistics"

    def handle(self, *args, **options):
        time = timezone.now().strftime("%X")

        self.update_teams_statistics()

        self.stdout.write(self.style.SUCCESS("Updated teams statistics at %s" % time))
        return

    def update_teams_statistics(self):
        teams = Team.objects.all()
        for team in teams:
            self.stdout.write(f"Checking team {team}")
            team.update_statistics()
