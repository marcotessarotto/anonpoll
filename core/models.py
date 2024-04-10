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
    def get_choices(self, randomize_choices=False):
        if randomize_choices:
            # Randomize the order of returned choices
            return self.choice_set.order_by('?')
        else:
            # Return choices in their default order
            return self.choice_set.all()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=512)
    votes = models.IntegerField(default=0)

    def __str__2(self):
        return f"id: {self.id} - choice_text: {self.choice_text} - votes: {self.votes}"

    def __str__(self):
        return f"{self.choice_text}"
