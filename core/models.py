import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Question(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))

    question_text = models.TextField(max_length=2000)

    start_time = models.DateTimeField('start time')  # Poll start time
    end_time = models.DateTimeField('end time')      # Poll end time

    slug = models.SlugField(max_length=255, unique=True)
    ref_token = models.UUIDField(default=uuid.uuid4)

    privacy_policy = models.TextField(blank=True, null=True)

    choices_are_sorted = models.BooleanField(default=True)

    enable_textfield_choice = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text

    # Optionally, you might want to add a method to check if the poll is currently active
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    # Modified method to get all choices related to this question
    # with an optional parameter to randomize the choices
    def get_choices(self, sorted=False):
        if not sorted:
            # Randomize the order of returned choices
            return self.choice_set.order_by('?')
        else:
            # Return choices in their default order
            return self.choice_set.order_by('choice_text')

    class Meta:
        verbose_name = _("Sondaggio")
        verbose_name_plural = _("Sondaggi")
        ordering = ('-created_at',)


class ChoiceSuggestedByUser(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=512)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.choice_text}"

    class Meta:
        verbose_name = _("Scelta suggerita dall'utente")
        verbose_name_plural = _("Scelte suggerite dagli utenti")
        ordering = ('choice_text',)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=512)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.choice_text}"

    def is_choice_text_user_defined(self):
        return self.choice_text == 'ZZZ_USER_DEFINED'

    class Meta:
        verbose_name = _("Scelta di sondaggio")
        verbose_name_plural = _("Scelte di sondaggio")
        ordering = ('-votes',)


class ChoiceVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    # voted_at = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name = _("Voto di un sondaggio")
        verbose_name_plural = _("Voti di sondaggi")
        ordering = ('-id',)


class ChoiceVoteSuggestedByUser(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(ChoiceSuggestedByUser, on_delete=models.CASCADE)
    # voted_at = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name = _("Voto di un sondaggio suggerito dall'utente")
        verbose_name_plural = _("Voti di sondaggi suggeriti dagli utenti")
        ordering = ('-id',)


def question_reset_votes(question):
    for choice in question.choice_set.all():
        choice.votes = 0
        choice.save()

    ChoiceVote.objects.filter(question=question).delete()
    ChoiceVoteSuggestedByUser.objects.filter(question=question).delete()

    ChoiceSuggestedByUser.objects.filter(question=question).delete()

