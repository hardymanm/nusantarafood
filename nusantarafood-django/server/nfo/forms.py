from django import forms

from nfo import models


class WordnetAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WordnetAnswer
        fields = ['word', 'correct_hypernym']


class WikiAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WikiAnswer
        fields = ['document', 'suggested_categories']


class TabelAnswerForm(forms.ModelForm):
    class Meta:
        model = models.TabelAnswer
        fields = ['document', 'correct_categories', 'suggested_categories']


class UploadJlForm(forms.Form):
    # dataset_name = forms.CharField(max_length=255)
    file = forms.FileField()