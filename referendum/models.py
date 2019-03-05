from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.

class Referendum(models.Model):
    """
    Referendum.
    """
    title = models.CharField(verbose_name="Titre du référendum", max_length=300)
    description = models.TextField(verbose_name="Description du référendum", max_length=10000)
    question = models.CharField(verbose_name="Question posée aux citoyens", max_length=300)
    Category = models.ManyToManyField("Category")
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de la dernière modification", auto_now=True)
    publication_date = models.DateTimeField(verbose_name="Date de publication", blank=True)
    event_start = models.DateTimeField(verbose_name="Début des votes", blank=True)
    event_end = models.DateTimeField(verbose_name="Fin des votes", blank=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Category is used to describe and organise referendums.
    """
    title = models.CharField(verbose_name="Titre de la catégorie", max_length=150)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class Choice(models.Model):
    """
    Choice is one option that a citizen can vote for a given referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Libellé du choix", max_length=150)

    def __str__(self):
        return f"{self.referendum}:{self.title}"


class Vote(models.Model):
    """
    Citizen's response to a referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    choice = models.ForeignKey("Choice", verbose_name="Valeur du vote", on_delete=models.CASCADE)
    vote_date = models.DateTimeField(verbose_name="Date de vote", auto_now_add=True)

    def __str__(self):
        return f"{self.choice} - {self.vote_date}"


class VoteToken(models.Model):
    """
    One instance of VoteToken is a single-use voter card.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    token = models.CharField(verbose_name="Token", max_length=150)
    voted = models.BooleanField(verbose_name="A voté ?", default=False)

    def __str__(self):
        return "{}: L'utilisateur {} {} en utilisant le token {}".format(
            self.referendum,
            self.user,
            "a voté" if self.voted else "n'a pas voté",
            self.token)


class Like(models.Model):
    """
    A testimony of interest from a citizen.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} s'intéresse au référendum: {self.referendum}."


class Comment(models.Model):
    """
    A comment from a citizen about a referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Texte du commentaire", max_length=10000)
    publication_date = models.DateTimeField(verbose_name="Date de publication du commentaire", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de dernière mise à jour du commentaire", auto_now=True)
    visible = models.BooleanField(verbose_name="Visible", default=True)

    def __str__(self):
        return f"{self.user} a commenté le référendum {self.referendum} le {self.publication_date} : {self.text}"


class Report(models.Model):
    """
    A report about an unapropriate comment.
    """
    comment = models.ForeignKey('Comment', verbose_name="Commentaire signalé", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Raison du signalement", max_length=1000)
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)

    def __str__(self):
        return f"Commentaire {self.comment_id} signalé le {self.creation_date}"
