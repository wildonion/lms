from django.urls import path

from cats.views import CatsListView, CatsCreateView, CatsEditView

app_name = 'cat_api'

urlpatterns = [
    path('all/', CatsListView.as_view(), name='list-cat'),
    path('create/', CatsCreateView.as_view(), name='create-cat'),
    # path('<pk>', CatsEditView.as_view(), name='list-cat'),
]
