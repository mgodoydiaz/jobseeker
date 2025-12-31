from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ya no necesitamos la vista de documentación estática aquí
    # path('', ApiDocsView.as_view(), name='api_docs'),
]
