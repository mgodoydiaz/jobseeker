from rest_framework import serializers
from .models import JobOffer, Application

class JobOfferSerializer(serializers.ModelSerializer):
    """
    Serializer for the JobOffer model.
    """
    class Meta:
        model = JobOffer
        fields = ('id', 'title', 'company', 'original_url', 'description', 'salary', 'published_date')
        read_only_fields = ('id',)

class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Application model.
    """
    job_offer = JobOfferSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'job_offer', 'status', 'application_date', 'notes')
        read_only_fields = ('id', 'application_date')
