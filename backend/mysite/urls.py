from django.contrib import admin
from django.urls import path
from job_postings.views import ApiDocsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ApiDocsView.as_view(), name='api_docs'),
]
