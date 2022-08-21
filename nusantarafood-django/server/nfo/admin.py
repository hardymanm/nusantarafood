from django.contrib import admin
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.admin import TokenAdmin
from nfo import models


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title']


class RecipeAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.Dataset)
admin.site.register(models.FoodCategory)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.LdaModel)
admin.site.register(models.Word)
admin.site.register(models.TabelEvaluation)
admin.site.register(models.WikiEvaluation)
admin.site.register(models.WordnetEvaluation)