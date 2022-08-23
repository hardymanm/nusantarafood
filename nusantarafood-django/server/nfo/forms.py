from django import forms

from nfo import models

class WordnetEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.WordnetEvaluation
        fields = ['word', 'correct_hypernym']
        
        
class WikiEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.WikiEvaluation
        fields = ['recipe', 'suggested_categories']
        

class TabelEvaluationForm(forms.ModelForm):
    class Meta:
        model = models.TabelEvaluation
        fields = ['recipe', 'correct_categories', 'suggested_categories']