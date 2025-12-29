from django.urls import path
from .views import CreateJobOfferView

urlpatterns = [
    path('job-offers/', CreateJobOfferView.as_view(), name='create-job-offer'),
]
