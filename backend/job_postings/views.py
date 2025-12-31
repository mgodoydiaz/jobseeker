from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = "index.html"

class ApiDocsView(TemplateView):
    template_name = "api_docs.html"
