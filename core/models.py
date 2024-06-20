import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class EventLog(models.Model):
    """
    Represents an event log entry.

    Args:
        event_type (str): The type of the event.
        event_title (str): The title of the event.
        event_data (str): The data associated with the event.
        event_target (str, optional): The target of the event.

    Returns:
        str: A string representation of the EventLog.

    Examples:
        >>> event = EventLog(event_type="LOGIN", event_title="User Login", event_data="User 'john' logged in successfully")
        >>> print(event)
        EventLog #1  event_type=LOGIN event_target=None event_title=User Login 2022-01-01 12:00:00
    """
    ERROR_SENDING_EMAIL = "ERROR_SENDING_EMAIL"
    EMAIL_SENT = "EMAIL_SENT"
    SUBSCRIPTION_SET = "SUBSCRIPTION_SET"
    SUBSCRIPTION_REMOVED = "SUBSCRIPTION_REMOVED"
    LOGIN = "LOGIN"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_SUCCESS_JSON = "LOGIN_SUCCESS_JSON"
    LOGIN_FAILED_JSON = "LOGIN_FAILED_JSON"
    REMAINDER_EMAIL_SENT = "REMAINDER_EMAIL_SENT"

    created_at = models.DateTimeField(auto_now_add=True)

    event_type = models.CharField(max_length=128, null=True)
    event_title = models.CharField(max_length=256, null=True)
    event_data = models.TextField(null=True)
    event_target = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return f"EventLog #{self.id}  event_type={self.event_type} event_target={self.event_target} event_title={self.event_title} {self.created_at}"


class Subscriber(models.Model):
    """
    Model for Subscriber, representing a subscriber with email, name, surname, and matricola.

    Attributes:
        email (str): The email of the subscriber.
        name (str): The name of the subscriber.
        surname (str): The surname of the subscriber.
        matricola (str): The matricola of the subscriber.

    Methods:
        __str__(): Returns a string representation of the Subscriber instance.
    """
    email = models.EmailField(verbose_name=_("Email"), max_length=255)
    name = models.CharField(verbose_name=_("Nome"), max_length=255)
    surname = models.CharField(verbose_name=_("Cognome"), max_length=255)
    matricola = models.CharField(verbose_name=_("Matricola"), max_length=255)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")


class Question(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))

    question_text = models.TextField(max_length=2000)

    start_time = models.DateTimeField('start time')  # Poll start time
    end_time = models.DateTimeField('end time')  # Poll end time

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


#**********************

class NamedSurvey(models.Model):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255, verbose_name=_("Nome"))

    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(verbose_name="Poll start time", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="Poll end time", null=True, blank=True)

    slug = models.SlugField(max_length=255, unique=True)
    ref_token = models.UUIDField(default=uuid.uuid4)

    privacy_policy = models.TextField(blank=True, null=True)

    info_text = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class NamedSurveyQuestion(models.Model):
    QUESTION_TYPES = [
        ('YNK', 'Sì/No/Non so'),
        ('TXT', 'Testo'),
        ('MCQ', 'Domanda a scelta multipla'),
        ('YN', 'Sì/No'),
    ]

    survey = models.ForeignKey(NamedSurvey, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=1024)
    question_type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='YNK')
    mandatory = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({self.get_question_type_display()})"


class NamedSurveyQuestionOption(models.Model):
    question = models.ForeignKey(NamedSurveyQuestion, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.option_text}"


class NamedSurveyResponse(models.Model):
    survey = models.ForeignKey(NamedSurvey, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Response on {self.created_at}"


class NamedSurveyAnswer(models.Model):
    response = models.ForeignKey(NamedSurveyResponse, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(NamedSurveyQuestion, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Answer to {self.question.text} - {self.text}"
