from django.urls import path

from .views import CommentListAPIView, CommentCreateAPIViewPost, CommentUpdateAPIView, CommentStatusAPIView

app_name = 'comment_api'

urlpatterns = [
    path('all/', CommentListAPIView.as_view(), name='list'),
    path('create/', CommentCreateAPIViewPost.as_view(), name='create'),
    path('<pk>', CommentUpdateAPIView.as_view(), name='edit'),
    path('status/<pk>', CommentStatusAPIView.as_view()),
]
