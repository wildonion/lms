from django.contrib import admin

# # Register your models here.
from .models import *


@admin.register(OTPModel)
class OTPModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'receptor', 'recent_code', 'login_counter', 'created_at', 'updated_at', 'otp_type']
    
    
@admin.register(GoogleMetaData)
class GoogleMetaDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'email', 'google_id', 'image_url',]
    
    
@admin.register(OTPMetaData)
class OTPMetaDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'otp_id', 'message_id', 'sent_date', 'cost', 'sender_number',]
    

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'image',]
    

@admin.register(ProfileUpdater)
class ProfileUpdaterAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'update_counter']
    
    
    
@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'points']