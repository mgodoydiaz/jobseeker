from django.contrib import admin
from .models import UserProfile, JobOffer, Application, ResumeTemplate

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'professional_summary')

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'published_date', 'created_at')
    search_fields = ('title', 'company', 'description')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_offer', 'status', 'application_date')
    list_filter = ('status', 'user')
    search_fields = ('job_offer__title', 'user__username')

@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at')
    list_filter = ('user',)
