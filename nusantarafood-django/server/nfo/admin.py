from django.contrib import admin
from nfo import models


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['title']


admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.Dataset)
admin.site.register(models.FoodCategory)
admin.site.register(models.Word)