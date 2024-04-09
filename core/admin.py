from django.contrib import admin
from .models import Question, Choice


class QuestionAdmin(admin.ModelAdmin):
    fields = ['question_text', 'pub_date', 'start_time', 'end_time']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
