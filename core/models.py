from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    start_time = models.DateTimeField('start time')  # Poll start time
    end_time = models.DateTimeField('end time')      # Poll end time

    def __str__(self):
        return self.question_text

    # Optionally, you might want to add a method to check if the poll is currently active
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_time <= now <= self.end_time


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
