from django.contrib import admin
from . import models

# Register your models here.
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'name', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('name', 'owner__username')
    ordering = ('-created_at',)


admin.site.register(models.Community, CommunityAdmin)
