from django import forms
from .models import Choice, NamedSurveyAnswer, NamedSurveyQuestionOption
from django.utils.translation import gettext_lazy as _
from .models import NamedSurveyQuestion

# class VoteFormV1(forms.Form):
#     choice = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)
#     accept_privacy_policy = forms.ChoiceField(choices=[('yes', 'Sì'), ('no', 'No')], label="Accetti la privacy policy?",
#                                               widget=forms.Select)
#
#     def __init__(self, *args, **kwargs):
#         question = kwargs.pop('question')
#         super().__init__(*args, **kwargs)
#         self.fields['choice'].queryset = question.get_choices(sorted=question.choices_are_sorted)


class VoteForm(forms.Form):  # WithTextField
    choice = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)
    text_choice = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Scrivi la tua scelta qui...'}))
    accept_privacy_policy = forms.ChoiceField(choices=[('scegli', 'scegli'), ('yes', 'Sì'), ('no', 'No')], label="Accetti la privacy policy?", widget=forms.Select)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = question.get_choices(sorted=question.choices_are_sorted)
        self.fields['choice'].required = True
        if not question.enable_textfield_choice:
            del self.fields['text_choice']  # Remove the text field if not enabled

    def is_valid(self):
        valid = super().is_valid()

        # print(f"Valid: {valid}")
        if not valid:
            return False

        choice = self.cleaned_data.get('choice', None)
        text_choice = self.cleaned_data.get('text_choice', None)

        # print(f"choice: {choice}")
        # print(f"text_choice: {text_choice}")
        #
        # print(f"self.cleaned_data: {self.cleaned_data}")

        if choice is None:
            self.add_error('choice', _('Choose an option.'))
            return False

        if choice.choice_text == 'ZZZ_USER_DEFINED':
            if text_choice is None or text_choice == '':
                self.add_error('text_choice', _('The text choice is required.'))
                return False
            else:
                # print("Text choice is valid")
                return True
        elif choice is not None:
            return True

        return False


class SubscriberLoginForm(forms.Form):

    matricola = forms.CharField(
        label='Matricola',
        max_length=255,
        widget=forms.TextInput(attrs={'size': '40'})  # Specify size for matricola field
    )

    email = forms.EmailField(
        label='Email regionale',
        widget=forms.EmailInput(attrs={'size': '40'})  # Here we specify the size
    )

#****************


class NamedSurveyAnswerForm(forms.ModelForm):
    class Meta:
        model = NamedSurveyAnswer
        fields = ['text']


TEXT_AREA_COLUMNS = 60
TEXT_AREA_ROWS = 4


# def make_named_survey_form(survey):
#     class PollForm(forms.Form):
#         def __init__(self, *args, **kwargs):
#             super().__init__(*args, **kwargs)
#             questions = NamedSurveyQuestion.objects.filter(survey=survey)
#             for question in questions:
#                 field_name = f"question_{question.id}"
#                 if question.question_type == 'YNK':
#                     choices = [('do_not_know', 'Do not know'), ('yes', 'Yes'), ('no', 'No')]
#                     self.fields[field_name] = forms.ChoiceField(
#                         choices=choices,
#                         label=question.text,
#                         widget=forms.Select,  # Changed from RadioSelect to Select
#                         initial='do_not_know'
#                     )
#                 elif question.question_type == 'TXT':
#                     self.fields[field_name] = forms.CharField(
#                         label=question.text,
#                         widget=forms.Textarea(attrs={'rows': 4}),
#                         required=False
#                     )
#
#     return PollForm


def make_named_survey_form(survey):
    class NamedSurveyForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            questions = NamedSurveyQuestion.objects.filter(survey=survey)
            for question in questions:
                field_name = f"question_{question.id}"
                # Get the required status from the 'mandatory' attribute of the question
                required_status = question.mandatory

                if question.question_type == 'YNK':
                    choices = [('do_not_know', 'Non lo so'), ('yes', 'Sì'), ('no', 'No')]
                    self.fields[field_name] = forms.ChoiceField(
                        choices=choices,
                        label=question.text,
                        widget=forms.Select,
                        initial='do_not_know',
                        required=required_status  # Set the required status based on the question's mandatory attribute
                    )
                elif question.question_type == 'YN':
                    choices = [('yes', 'Sì'), ('no', 'No')]
                    self.fields[field_name] = forms.ChoiceField(
                        choices=choices,
                        label=question.text,
                        widget=forms.Select,
                        required=required_status  # Apply the mandatory attribute
                    )
                elif question.question_type == 'TXT':
                    self.fields[field_name] = forms.CharField(
                        label=question.text,
                        widget=forms.Textarea(attrs={'rows': 4}),
                        required=required_status  # Apply the mandatory attribute
                    )
                elif question.question_type == 'MCQ':
                    # Fetch the options related to the current question
                    options = NamedSurveyQuestionOption.objects.filter(question=question)
                    choices = [(option.id, option.option_text) for option in options]
                    self.fields[field_name] = forms.ChoiceField(
                        choices=choices,
                        label=question.text,
                        widget=forms.Select,
                        required=required_status  # Apply the mandatory attribute
                    )

    return NamedSurveyForm
