from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import JobOffer, UserProfile
from .serializers import JobOfferSerializer
from .llm_utils import analyze_job_match

class CreateJobOfferView(generics.CreateAPIView):
    """
    API view to create a new job offer.
    If a job offer with the same original_url already exists, it returns the existing one.
    After creating a new offer, it triggers an LLM analysis to match it against the user's profile.
    """
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    # Require the user to be authenticated to create a job offer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Save the new JobOffer and then trigger the LLM analysis.
        """
        # First, save the initial job offer to get an instance
        job_offer = serializer.save()

        # --- Trigger LLM Analysis ---
        try:
            user = self.request.user
            # We assume the user has a UserProfile. In a real app, you might want to create it if it doesn't exist.
            user_profile = UserProfile.objects.get(user=user)
            user_experience = user_profile.professional_summary
            job_description = job_offer.description

            # Only run analysis if we have the necessary data
            if user_experience and job_description:
                print(f"--- Triggering LLM analysis for offer: {job_offer.title} ---")
                
                # Call the (simulated) LLM analysis function
                analysis_results = analyze_job_match(user_experience, job_description)

                # Update the job offer instance with the analysis results
                job_offer.summary = analysis_results.get('summary')
                job_offer.match_score = analysis_results.get('match_score')
                # The analysis returns a list, but the model expects a text field
                job_offer.missing_skills = str(analysis_results.get('missing_skills', []))
                
                # Save the updated instance
                job_offer.save()
                print(f"--- LLM analysis saved for offer: {job_offer.title} ---")
            else:
                print("--- LLM analysis skipped: User experience or job description is missing. ---")

        except UserProfile.DoesNotExist:
            print(f"--- LLM analysis skipped: UserProfile for {user.username} not found. ---")
        except Exception as e:
            # We log the error but don't want to fail the entire request just because the analysis failed.
            print(f"An error occurred during the LLM analysis step: {e}")

    def create(self, request, *args, **kwargs):
        """
        Handle the creation of a new job offer or return an existing one.
        """
        original_url = request.data.get('original_url')

        # If a URL is provided, check if an offer already exists
        if original_url:
            try:
                job_offer = JobOffer.objects.get(original_url=original_url)
                serializer = self.get_serializer(job_offer)
                # If it exists, we just return it without creating a new one.
                return Response(serializer.data, status=status.HTTP_200_OK)
            except JobOffer.DoesNotExist:
                # If it does not exist, we proceed to create a new one.
                pass
        
        # The call to super().create() will trigger perform_create() after validation
        return super().create(request, *args, **kwargs)
