from django.urls import path

from .views import CourseEditView, CourseListView, AuthorCourseList, CourseCreateView, AllCourseListView, \
    CourseChangeStatusView, UploadVideoView, VideoListView, VideoDetailView, PrerequisiteEditView, PrerequisiteCreateView, \
    PrerequisiteListView, User_CourseEditView, User_CourseCreateView, User_CourseListView, CourseVideoListView, UserVideoView, UserVideosView

app_name = 'Course_api'

urlpatterns = [

    path('published/', CourseListView.as_view(), name='list'), # NOTE - get all published courses
    path('all/', AllCourseListView.as_view(), name='list-all'),
    path('create/', CourseCreateView.as_view(), name='create'),
    path('author/', AuthorCourseList.as_view(), name='authorProductList'),
    path('<slug>', CourseEditView.as_view(), name='listcreate'),
    path('status/<slug>', CourseChangeStatusView.as_view(), name='soft-del'),

    path('videos/all/', VideoListView.as_view(), name='video-list'),
    path('videos/upload/', UploadVideoView.as_view(), name='PostVideo'),
    path('videos/<pk>', VideoDetailView.as_view(), name='video_detail'),
    path('videos/', CourseVideoListView.as_view(), name='course_video_detail'), # NOTE - list of all videos for a course

    path('user/video/<pk>', UserVideoView.as_view(), name='user_video'), # NOTE - pk is the video id - get a single user video info
    path('user/videos/', UserVideosView.as_view(), name='user_videos'), # NOTE - get all user videos info
    path('user/', User_CourseListView.as_view(), name='list-user_course'),
    path('user/create/', User_CourseCreateView.as_view(), name='create-user_course'),
    path('user/<pk>', User_CourseEditView.as_view(), name='list-user_course'),

    path('prerequisites/<slug>', PrerequisiteEditView.as_view(), name='edit-prerequisite'),
    path('prerequisites/create/', PrerequisiteCreateView.as_view(), name='create-prerequisite'),
    path('prerequisites/all/', PrerequisiteListView.as_view(), name='list-prerequisite'),
]
