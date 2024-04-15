from django import forms
from .models import Choice
from django.utils.translation import gettext_lazy as _

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

