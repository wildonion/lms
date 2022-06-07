


from django.urls import include, path
from .views import funquiz_update,get_all_results,get_funquiz,add_user_funquiz_result,add_user_email, get_user_last_funquiz



urlpatterns = [
    path('update/', funquiz_update),
    path('get/', get_funquiz),
    path('get/last/', get_user_last_funquiz),
    path('results/', get_all_results),
    path('add/result/', add_user_funquiz_result),
    path('add/user/email/', add_user_email),
]