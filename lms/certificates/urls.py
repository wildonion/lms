from django.urls import path

from .views import CertificateCreateView, CertificateListView, CertificateEditView

app_name = 'certificate-api'
urlpatterns = [
    path('all/', CertificateListView.as_view()),
    path('create/', CertificateCreateView.as_view()),
    path('<pk>', CertificateEditView.as_view()),

]
