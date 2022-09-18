from django import forms

from nfo import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm


class WordnetAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WordnetAnswer
        fields = ['word', 'correct_hypernym']


class WikiAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WikiAnswer
        fields = ['document', 'correct_categories']


class TabelAnswerForm(forms.ModelForm):
    class Meta:
        model = models.TabelAnswer
        fields = ['document', 'correct_categories']


class UploadDatasetForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class UploadWikiForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))


class AddJudgeForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            judge_group, _ = Group.objects.get_or_create(name='judge')
            judge_group.user_set.add(user)

        return user