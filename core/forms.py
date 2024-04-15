from django import forms
from .models import Choice


class VoteFormV1(forms.Form):
    choice = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)
    accept_privacy_policy = forms.ChoiceField(choices=[('yes', 'Sì'), ('no', 'No')], label="Accetti la privacy policy?",
                                              widget=forms.Select)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = question.get_choices(sorted=question.choices_are_sorted)


class VoteForm(forms.Form):  # WithTextField
    choice = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)
    text_choice = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter your choice'}))
    accept_privacy_policy = forms.ChoiceField(choices=[('yes', 'Sì'), ('no', 'No')], label="Accetti la privacy policy?", widget=forms.Select)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = question.get_choices(sorted=question.choices_are_sorted)
        self.fields['choice'].required = True
        if not question.enable_textfield_choice:
            del self.fields['text_choice']  # Remove the text field if not enabled

    def is_valid(self):
        valid = super().is_valid()

        print(f"Valid: {valid}")
        if not valid:
            return False
        if 'text_choice' in self.cleaned_data and self.cleaned_data['text_choice']:
            return True
        return False

