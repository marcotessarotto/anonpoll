from django import forms
from .models import Choice


class VoteForm(forms.Form):
    choice = forms.ModelChoiceField(queryset=None, widget=forms.RadioSelect, empty_label=None)
    accept_privacy_policy = forms.ChoiceField(choices=[('yes', 'Sì'), ('no', 'No')], label="Accetti la privacy policy?",
                                              widget=forms.Select)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super().__init__(*args, **kwargs)
        self.fields['choice'].queryset = question.get_choices(sorted=question.choices_are_sorted)
