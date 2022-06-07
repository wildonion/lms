





from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from users.views import (
                         get_all_users,
                         user_edit_password,
                         user_upload_profile,
                         user_login,
                         user_google_login,
                         user_otp_login,
                         send_signup_otp_request,
                         signup_otp_updater,
                         send_forgot_password_otp_request,
                         check_token,
                         user_edit_profile,
                         user_update_group,
                         user_update_status
                    ) 




urlpatterns = [
     
     
     path('otp-req/forgot-password/', send_forgot_password_otp_request), # NOTE - OTP req forgot password login
     path('otp-req/signup/', send_signup_otp_request), # NOTE - OTP req signup
     path('signup/otp/', signup_otp_updater), # NOTE - OTP signup
     path('profile/edit/', user_edit_profile), # NOTE - edit profile
     path('profile/edit/password/', user_edit_password), # NOTE - update password
     path('profile/edit/group/', user_update_group), # NOTE - update group
     path('profile/edit/status/', user_update_status), # NOTE - update status
     path('profile/upload/', user_upload_profile), # NOTE - update image profile
     path('login/', user_login), # NOTE - login with username and password
     path('login/otp/', user_otp_login), # NOTE - OTP login in case of forgot password
     path('login/google/', user_google_login), # NOTE - login with google and it'll return access and refresh tokens
     path('check-token/', check_token), # NOTE - check token for OTP, simple and google login
     path('get/all/', get_all_users)

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)