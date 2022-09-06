from django.contrib import admin
from nfo import models


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.Dataset)
admin.site.register(models.FoodCategory)
admin.site.register(models.Word)
admin.site.register(models.WordnetSession)
admin.site.register(models.WikiSession)
admin.site.register(models.TabelSession)
admin.site.register(models.WordnetAnswer)
admin.site.register(models.WikiAnswer)
admin.site.register(models.TabelAnswer)
admin.site.register(models.Tabel)