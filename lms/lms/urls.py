"""lms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import login
from django.urls import path
from django.urls.conf import include
from users.views import check_media
from django.urls import re_path
from django.conf.urls import url



urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls')),
    path('quiz/', include('quizzes.urls')),
    path('funquiz/', include('funquiz.urls')),
    path('user/', include('users.urls')),
    path('product/', include('products.urls')),
    path('certificate/', include('certificates.urls', namespace='certificate-api')),
    path('post/', include('posts.urls', namespace='posts-api')),
    path('course/', include('courses.urls', namespace='course-api')),
    path('comment/', include('comments.urls', namespace='comment-api')),
    path('cat/', include('cats.urls', namespace='cat-api')),
    path('ticket/', include('tickets.urls', namespace='ticket-api')),
    path('proposal/', include('proposal.urls', namespace='proposal-api')),
    path('media/videos/courses/', check_media, name='check-media'),
]