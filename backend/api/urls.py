from django.urls import path
from .views import RegisterView, LoginView, MessageView, end_session, get_audio_message

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('message/', MessageView.as_view(), name='message'),
    path('end-session/', end_session, name='end-session'),
    path('send-audio/', get_audio_message, name='send-audio'),
]
