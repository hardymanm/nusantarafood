from django.contrib import admin

from nfo import models


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title', 'title_clean']


# Register your models here.
admin.site.register(models.TokenList)
admin.site.register(models.Tabel)
admin.site.register(models.Dataset)
admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.Word)
admin.site.register(models.FoodCategory)
admin.site.register(models.JudgeSession)
admin.site.register(models.WordnetAnswer)
admin.site.register(models.WikiAnswer)
admin.site.register(models.TabelAnswer)
admin.site.register(models.Ingredient)
admin.site.register(models.Variation)
admin.site.register(models.WordnetAccuracy)