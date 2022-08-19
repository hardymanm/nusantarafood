from django.contrib import admin
from nfo import models

admin.site.register(models.Judge)
admin.site.register(models.Document)
admin.site.register(models.Dataset)
admin.site.register(models.FoodCategory)
admin.site.register(models.Recipe)
admin.site.register(models.LdaModel)
admin.site.register(models.Word)
admin.site.register(models.TabelEvaluation)
admin.site.register(models.WikiEvaluation)