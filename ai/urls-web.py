from django.urls import path

from ai.views import PostAiAPIView

app_name = 'ai'

urlpatterns = [
    path('post-detail/', PostAiAPIView.as_view())
]