from django import forms

from nfo import models

class WordnetEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.WordnetEvaluation
        fields = ['word', 'correct_hypernym']