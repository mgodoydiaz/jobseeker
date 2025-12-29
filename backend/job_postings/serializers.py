
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, JobOffer, Application, ResumeTemplate

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('professional_summary',)

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')

class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    # Make job_offer writeable by id, but readable as a nested object
    job_offer = JobOfferSerializer(read_only=True)
    job_offer_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Application
        fields = ('id', 'job_offer', 'job_offer_id', 'status', 'application_date', 'notes')

    def create(self, validated_data):
        # Associate the application with the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ResumeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeTemplate
        fields = '__all__'
        read_only_fields = ('user',)

    def create(self, validated_data):
        # Associate the template with the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
