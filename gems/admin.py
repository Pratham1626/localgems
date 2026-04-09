from django.contrib import admin
from .models import Gem, OpenCall, Application

@admin.register(Gem)
class GemAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'category', 'city', 'rating', 'is_featured']
    list_filter = ['category', 'is_featured']
    search_fields = ['stage_name', 'user__email']
    list_editable = ['is_featured']

@admin.register(OpenCall)
class OpenCallAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'budget', 'category', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'open_call', 'applied_at']
    list_filter = ['open_call']
