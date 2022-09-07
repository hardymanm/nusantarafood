from django.contrib import admin

from nfo import models

# Register your models here.
admin.site.register(models.Stopword)
admin.site.register(models.Tabel)
admin.site.register(models.Dataset)
admin.site.register(models.Document)
admin.site.register(models.Word)
admin.site.register(models.FoodCategory)
admin.site.register(models.JudgeSession)
admin.site.register(models.WordnetAnswer)
admin.site.register(models.WikiAnswer)
admin.site.register(models.TabelAnswer)
