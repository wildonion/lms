





from django.urls import include, path
from .views import quizz_create, get_quizzes, get_teacher_quizzes, quizz_update, get_quizz, get_user_quizz, update_user_quizz








urlpatterns = [
    path('create/', quizz_create),
    path('all/', get_quizzes),
    path('author/', get_teacher_quizzes),
    path('update/', quizz_update),
    path('user/get/', get_user_quizz),
    path('user/update/', update_user_quizz),
    path('', get_quizz)
]