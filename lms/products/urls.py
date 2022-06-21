from django.urls import path

from .views import ProductCreateView, ProductListView, ProductRetrieveUpdateView, DiscountListView, DiscountCreateView, DiscountCreateUserView, \
    DiscountRetrieveUpdateView, CheckDiscount, load_more, expire_discount, load_course_by_level, load_quiz, search

urlpatterns = [
    path('all/', ProductListView.as_view()),
    path('create/', ProductCreateView.as_view()),
    path('<pk>', ProductRetrieveUpdateView.as_view(), name='listcreate'),
    path('load-more/', load_more),
    path('load-course/', load_course_by_level),
    path('load-quiz/', load_quiz),
    path('search/', search),

    path('discount/all/', DiscountListView.as_view()),
    path('discount/create/', DiscountCreateView.as_view()),
    path('discount/create/by-user', DiscountCreateUserView.as_view()),
    path('discount/<pk>', DiscountRetrieveUpdateView.as_view()),
    path('discount/check/', CheckDiscount.as_view()),
    path('discount/set-expire/', expire_discount),
]
