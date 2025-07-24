from django.urls import path
from .views import ChatMessageListCreateView

urlpatterns = [
    path('messages/', ChatMessageListCreateView.as_view(), name='chatmessage-list-create'),
]
