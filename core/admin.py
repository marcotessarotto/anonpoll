from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Question, Choice, ChoiceVote, ChoiceSuggestedByUser, ChoiceVoteSuggestedByUser


class QuestionAdmin(admin.ModelAdmin):
    # Displaying fields in the list view
    list_display = ('name', 'start_time', 'end_time', 'is_active', 'created_at', 'updated_at')
    # Adding a search field
    search_fields = ['name', 'question_text']
    # Adding filters
    list_filter = ('start_time', 'end_time', 'created_at', 'updated_at')
    # Adding fieldsets for structured form layout
    fieldsets = (
        (_('Question Information'), {'fields': ('name', 'question_text', 'slug', 'ref_token', 'privacy_policy','choices_are_sorted', 'enable_textfield_choice')}),
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
    list_display = ('question', 'choice', 'voted_at')
    list_filter = ('question', 'choice', 'voted_at')
    search_fields = ('question__text', 'choice__choice_text', 'voted_at')
    date_hierarchy = 'voted_at'
    ordering = ('-voted_at',)

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
    list_display = ('question', 'choice', 'voted_at')  # Display these fields in the admin list view
    list_filter = ('question', 'choice', 'voted_at')  # Enable filtering by these fields
    search_fields = ('question__text', 'choice__choice_text')  # Search by question text and choice text
    date_hierarchy = 'voted_at'  # Provide a drill-down by date

admin.site.register(ChoiceVoteSuggestedByUser, ChoiceVoteSuggestedByUserAdmin)

