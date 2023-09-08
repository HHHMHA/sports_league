from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .services import GameService


class ImportGamesForm(forms.Form):
    file = forms.FileField(
        allow_empty_file=False,
        required=True,
    )

    def clean(self, commit=True):
        result = GameService.import_games_from_csv(self.cleaned_data["file"])
        if not result:
            raise ValidationError(_("Could not import games from provided file"))
        return self.cleaned_data
