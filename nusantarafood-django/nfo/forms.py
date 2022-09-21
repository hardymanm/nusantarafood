from django import forms
from django.db import transaction
from nfo import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm


class RenameDatasetForm(forms.ModelForm):
    class Meta:
        model = models.Dataset
        fields = ['name']


class SplitDatasetForm(forms.ModelForm):
    size = forms.IntegerField(min_value=1)

    class Meta:
        model = models.Dataset
        fields = ['name', 'size']

    def clean(self):
        cleaned_data = super().clean()
        size = cleaned_data.get('size')
        name = cleaned_data.get('name')

        max_size = self.instance.document_set.count() - 1
        if size > max_size:
            raise forms.ValidationError('Size is bigger than document count')
        if name == self.instance.name:
            raise forms.ValidationError('Dataset name already taken')

        return cleaned_data


class JoinDatasetForm(forms.Form):
    datasets = forms.ModelMultipleChoiceField(queryset=models.Dataset.objects.order_by('name').all())


class WordnetAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WordnetAnswer
        fields = ['word', 'correct_hypernym']


class WikiAnswerForm(forms.ModelForm):
    class Meta:
        model = models.WikiAnswer
        fields = ['suggested_categories']


class TabelAnswerForm(forms.ModelForm):
    class Meta:
        model = models.TabelAnswer
        fields = ['correct_categories', 'suggested_categories']


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


class IngredientForm(forms.Form):
    ingredient = forms.CharField()
    variation = forms.CharField(widget=forms.Textarea(attrs={'name': 'variation', 'rows': '10'}))

    def save(self):
        if self.is_valid():
            name = self.cleaned_data.get('ingredient')
            with transaction.atomic():
                ingredient, _ = models.Ingredient.objects.get_or_create(name=name)

                variation = self.cleaned_data.get('variation')
                variations = variation.splitlines()
                variations = [i.strip() for i in variations]

                # Include ingredient as variation
                obj, _ = models.Variation.objects.get_or_create(ingredient=ingredient, name=name)

                # The rest of variations
                for variation in variations:
                    obj, _ = models.Variation.objects.get_or_create(ingredient=ingredient, name=variation)

        else:
            raise forms.ValidationError('invalid form')
