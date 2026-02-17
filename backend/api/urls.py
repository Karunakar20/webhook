from django.urls import path, include
from api.views.webhook_views import WebhookView

urlpatterns = [
    path('webhook/', WebhookView.as_view()),
]
