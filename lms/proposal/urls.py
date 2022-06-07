# from django.urls import path
from django.urls import path

from proposal.views import ProposalListAPIView, ProposalCreateAPIView, ProposalEditAPIView, ProposalChangeStatus, \
    AllProposalListAPIView, ckeditor_upload_image, ckeditor_upload_video

app_name = 'proposal_api'

urlpatterns = [

    path('published/', ProposalListAPIView.as_view(), name='list'),
    path('all/', AllProposalListAPIView.as_view(), name='all-list'),
    path('<slug>', ProposalEditAPIView.as_view(), name='detail'),
    path('create/', ProposalCreateAPIView.as_view(), name='create'),
    path('status/<slug>', ProposalChangeStatus.as_view(), name='status'),
    path('ck-img/', ckeditor_upload_image),
    path('ck-vid/', ckeditor_upload_video),
]
