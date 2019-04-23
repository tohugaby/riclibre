"""
Referendum's app:  Comment's models
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


class Comment(models.Model):
    """
    A comment from a citizen about a referendum.
    """
    referendum = models.ForeignKey("referendum.Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Texte du commentaire", max_length=10000)
    publication_date = models.DateTimeField(verbose_name="Date de publication du commentaire", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de dernière mise à jour du commentaire", auto_now=True)
    visible = models.BooleanField(verbose_name="Visible", default=True)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-publication_date', ]

    def __str__(self):
        return f"{self.user} a commenté le référendum {self.referendum} le {self.publication_date} : {self.text}"

    def get_absolute_url(self):
        return "%s#comment_%s" % (reverse('referendum', kwargs={'slug': self.referendum.slug}), self.pk)

    @property
    def update_url(self):
        """
        Instance update url.
        """
        return reverse('comment_update', kwargs={'pk': self.pk})


class Report(models.Model):
    """
    A report about an unapropriate comment.
    """
    comment = models.ForeignKey('Comment', verbose_name="Commentaire signalé", on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), verbose_name="Citoyen", on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Raison du signalement", max_length=1000)
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"

    def __str__(self):
        return f"Commentaire {self.comment_id} signalé le {self.creation_date}"
