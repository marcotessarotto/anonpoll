from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from .models import Question, Choice, ChoiceVote, ChoiceSuggestedByUser, ChoiceVoteSuggestedByUser, EventLog, \
    Subscriber, NamedSurveyQuestionOption
from .models import NamedSurvey, NamedSurveyQuestion, NamedSurveyResponse, NamedSurveyAnswer


from openpyxl import Workbook


def export_named_survey_answers_to_excel(modeladmin, request, queryset):
    # Create a workbook and add a worksheet.
    wb = Workbook()
    ws = wb.active
    ws.title = "Survey Answers"

    # Define the header
    columns = ['Survey Title', 'Question', 'Answer', 'Subscriber Email', 'Subscriber Name', 'Subscriber Surname']
    ws.append(columns)

    # Append data rows
    for answer in queryset:
        subscriber = answer.response.subscriber
        row = [
            answer.response.survey.title,
            answer.question.text,
            answer.text or "No Answer",
            subscriber.email if subscriber else "No Subscriber",
            subscriber.name if subscriber else "No Name",
            subscriber.surname if subscriber else "No Surname"
        ]
        ws.append(row)

    # Prepare the HTTP response with the appropriate headers
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="named_survey_answers.xlsx"'

    # Save the workbook to the response
    wb.save(response)

    return response


export_named_survey_answers_to_excel.short_description = "Export Selected Answers to Excel"


class QuestionAdmin(admin.ModelAdmin):
    # Displaying fields in the list view
    list_display = ('name', 'start_time', 'end_time', 'is_active', 'created_at', 'updated_at')
    # Adding a search field
    search_fields = ['name', 'question_text']
    # Adding filters
    list_filter = ('start_time', 'end_time', 'created_at', 'updated_at')
    # Adding fieldsets for structured form layout
    fieldsets = (
        (_('Question Information'), {'fields': (
            'name', 'question_text', 'slug', 'ref_token', 'privacy_policy', 'choices_are_sorted',
            'enable_textfield_choice')}),
        (_('Timing'), {'fields': ('start_time', 'end_time')}),
        (_('Metadata'), {'fields': ('created_at', 'updated_at')}),
    )
    # Setting readonly fields
    readonly_fields = ('created_at', 'updated_at')
    # Customizing the slug field to be generated based on the question name
    prepopulated_fields = {"slug": ("name",)}

    # You can also override the save_model method if you need custom behavior when saving an object from the admin
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    # Adding the 'is_active' method to list_display requires us to help Django determine
    # how to order results. Here, we arbitrarily choose to order by 'start_time' when sorting by 'is_active'.
    def get_ordering(self, request):
        ordering = super().get_ordering(request)
        if 'is_active' in request.GET.get('o', ''):
            return ('start_time',)
        return ordering


admin.site.register(Question, QuestionAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'votes', 'question')
    list_filter = ('question',)
    search_fields = ('choice_text',)
    raw_id_fields = ('question',)

    def view_question_text(self, obj):
        return obj.question.question_text

    view_question_text.short_description = 'Question Text'


admin.site.register(Choice, ChoiceAdmin)


class ChoiceVoteAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice',)
    list_filter = ('question', 'choice',)
    search_fields = ('question__text', 'choice__choice_text',)
    ordering = ('-id',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ChoiceVoteAdmin, self).get_form(request, obj, **kwargs)
        # Customizations here
        return form


admin.site.register(ChoiceVote, ChoiceVoteAdmin)


class ChoiceSuggestedByUserAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'votes')  # Fields to display in the admin list view
    list_filter = ('question',)  # Allow filtering by the question
    search_fields = (
        'choice_text', 'question__text')  # Enable a search box that searches the choice text and related question text


admin.site.register(ChoiceSuggestedByUser, ChoiceSuggestedByUserAdmin)


class ChoiceVoteSuggestedByUserAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice',)  # Display these fields in the admin list view
    list_filter = ('question', 'choice',)  # Enable filtering by these fields
    search_fields = ('question__text', 'choice__choice_text')  # Search by question text and choice text
    ordering = ('-id',)


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'event_type', 'event_title', 'event_target', 'event_data', 'created_at')
    list_filter = ['event_type']


admin.site.register(ChoiceVoteSuggestedByUser, ChoiceVoteSuggestedByUserAdmin)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'matricola')
    list_filter = ('name', 'surname')
    search_fields = ('email', 'name', 'surname', 'matricola')


class NamedSurveyQuestionOptionInline(admin.TabularInline):
    model = NamedSurveyQuestionOption
    extra = 1


@admin.register(NamedSurvey)
class NamedSurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'start_date', 'end_date', 'is_active')
    search_fields = ('title', 'name')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(NamedSurveyQuestion)
class NamedSurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'survey')
    list_filter = ('question_type', 'survey')
    inlines = [NamedSurveyQuestionOptionInline]


@admin.register(NamedSurveyResponse)
class NamedSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('survey', 'subscriber', 'created_at')
    list_filter = ('survey', 'created_at')


@admin.register(NamedSurveyAnswer)
class NamedSurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'text')
    search_fields = ('text', 'question__text')
    list_filter = ('response__survey', 'question')
    actions = [export_named_survey_answers_to_excel]  #