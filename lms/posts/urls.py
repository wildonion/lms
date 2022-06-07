# from django.urls import path
from django.urls import path

from posts.views import PostListAPIView, PostCreateAPIView, PostEditAPIView, PostChangeStatus, \
    AllPostListAPIView, ckeditor_upload_image, ckeditor_upload_video, post_categ, load_more, search_by_tag

app_name = 'post_api'

urlpatterns = [
    path('cat/', post_categ),
    path('search/tag/', search_by_tag),
    path('load-more/', load_more),
    path('published/', PostListAPIView.as_view(), name='list'),
    path('all/', AllPostListAPIView.as_view(), name='all-list'),
    path('<slug>', PostEditAPIView.as_view(), name='detail'),
    path('create/', PostCreateAPIView.as_view(), name='create'),
    path('status/<slug>', PostChangeStatus.as_view(), name='status'),
    path('ck-img/', ckeditor_upload_image),
    path('ck-vid/', ckeditor_upload_video),
]
