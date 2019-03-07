from django.db import models


class Referendum(models.Model):
    """
    Referendum.
    """
    title = models.CharField(verbose_name="Titre du référendum", max_length=300)
    description = models.TextField(verbose_name="Description du référendum", max_length=10000)
    question = models.CharField(verbose_name="Question posée aux citoyens", max_length=300)
    categories = models.ManyToManyField("Category")
    creation_date = models.DateTimeField(verbose_name="Date de création", auto_now_add=True)
    last_update = models.DateTimeField(verbose_name="Date de la dernière modification", auto_now=True)
    publication_date = models.DateTimeField(verbose_name="Date de publication", blank=True, null=True)
    event_start = models.DateTimeField(verbose_name="Début des votes", blank=True, null=True)
    event_end = models.DateTimeField(verbose_name="Fin des votes", blank=True, null=True)

    class Meta:
        verbose_name = "Référendum"
        verbose_name_plural = "Référendums"

    def __str__(self):
        return self.title

    @property
    def nb_votes(self):
        """
        The number of votes for this referendum.
        :return: a number of votes
        """
        return self.vote_set.count()


class Category(models.Model):
    """
    Category is used to describe and organise referendums.
    """
    title = models.CharField(verbose_name="Titre de la catégorie", max_length=150)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.title


class Choice(models.Model):
    """
    Choice is one option that a citizen can vote for a given referendum.
    """
    referendum = models.ForeignKey("Referendum", verbose_name="Référendum", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Libellé du choix", max_length=150)

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"

    def __str__(self):
        return f"{self.referendum}:{self.title}"

    @property
    def nb_votes(self):
        """
        The number of votes for this choice.
        :return: a number of votes
        """
        return self.vote_set.count()

    @property
    def votes_percentage(self):
        """
        The percentage of votes for this choice.
        :return: percentage of votes.
        """
        percentage = 0
        if self.referendum.nb_votes:
            percentage = (self.nb_votes / self.referendum.nb_votes) * 100
        return percentage
