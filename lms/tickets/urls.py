from django.urls import path

from .views import TicketListAPIView, TicketUpdateAPIView, TicketStatusAPIView, TicketCreateAPIViewPost

app_name = 'ticket_api'

urlpatterns = [
    path('all/', TicketListAPIView.as_view(), name='list'),
    path('create/', TicketCreateAPIViewPost.as_view(), name='create'),
    path('<pk>', TicketUpdateAPIView.as_view(), name='edit'),
    path('status/<pk>', TicketStatusAPIView.as_view()),
]
