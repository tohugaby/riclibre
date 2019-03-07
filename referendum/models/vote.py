from django.contrib.auth import get_user_model
from django.db import models


class Vote(models.Model):
    """
    Citizen's response to a referendum.
    """
    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    choice = models.ForeignKey("referendum.Choice", verbose_name="Valeur du vote", on_delete=models.CASCADE)
    vote_date = models.DateTimeField(verbose_name="Date de vote", auto_now_add=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

    def __str__(self):
        return f"{self.choice} - {self.vote_date}"


class VoteToken(models.Model):
    """
    One instance of VoteToken is a single-use voter card.
    """
    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    token = models.CharField(verbose_name="Token", max_length=150)
    voted = models.BooleanField(verbose_name="A voté ?", default=False)

    class Meta:
        verbose_name = "Token de vote"
        verbose_name_plural = "Tokens de vote"

    def __str__(self):
        return "{}: L'utilisateur {} {} en utilisant le token {}".format(
            self.referendum,
            self.user,
            "a voté" if self.voted else "n'a pas voté",
            self.token)
