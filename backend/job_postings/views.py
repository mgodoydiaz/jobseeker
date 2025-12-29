from rest_framework import viewsets
from .models import JobPosting
from .serializers import JobPostingSerializer

class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
