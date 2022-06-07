








from functools import reduce
from xml.etree.ElementPath import find
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from .models import *
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import requests
from django.conf import settings
import random, time
from datetime import datetime
from django.db.models.query_utils import Q









# ------------------------------
# --- Update Status Serializer
# ------------------------------
# --------------=============--------------=============--------------=============--------------=============
class StatusSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)  # NOTE - don't set write_only=True
    user_status = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def update(self, instance, validated_data):
        user_info = {}
        find_user = User.objects.filter(id=validated_data["user_id"])
        if find_user.exists():
            changed_status = True if int(validated_data["user_status"]) == 1 else False
            find_user.update(is_active=changed_status)
            user_info["user_id"] = instance.id
            user_info["username"] = instance.username
            user_info["user_status"] = find_user.first().is_active
        return {'message': "Updated successfully", "data": user_info}
# --------------=============--------------=============--------------=============--------------=============


# -------------------------
# --- Update Group Serializer
# -------------------------
# --------------=============--------------=============--------------=============--------------=============
class GroupSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)  # NOTE - don't set write_only=True
    user_group = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def update(self, instance, validated_data):
        user_info = {}
        new_group, created = Group.objects.get_or_create(name=validated_data["user_group"])
        group = new_group if new_group else created
        groups_list = ["superuser", "teacher", "student", "admin"]
        current_user_group = instance.groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups_list]))
        if current_user_group.exists():
            current_user_group.first().user_set.remove(instance)
            group.user_set.add(instance)
            user_group = instance.groups.filter(name=validated_data["user_group"])
            if user_group.exists():
                user_info["group_name"] = user_group.first().name 
            user_info["user_id"] = instance.id
            user_info["username"] = instance.username
            user_info["email"] = instance.email
            return {'message': "Updated successfully", "data": user_info}
        else:
            return {'message': "Can't find current user group", "data": []}
# --------------=============--------------=============--------------=============--------------=============


# -------------------------
# --- Upload Password Serializer
# -------------------------
# --------------=============--------------=============--------------=============--------------=============
class PasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True) # NOTE - don't set write_only=True  

    class Meta:
        model = User
        fields = ["password"]
    
    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        user_info = {"user_id": instance.id, "username": instance.username, "email": instance.email}
        return {'message': "Updated successfully", "data": user_info}
# --------------=============--------------=============--------------=============--------------=============


# -------------------------
# --- Upload Image Serializer
# -------------------------
# --------------=============--------------=============--------------=============--------------=============
class ImageSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=True)
    image = serializers.ImageField(required=True, use_url=True)
    
    class Meta:
        model = Profile
        fields = ["user_id", "image"]    

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        profile_info = {"user_id": instance.user_id, "image_name": instance.image.name, "image_path": instance.image.path, "image_url": instance.image.url}
        return {'message': "Uploaded successfully", "data": profile_info}
# --------------=============--------------=============--------------=============--------------=============


# --------------=============--------------=============--------------=============--------------=============


# ----------------------------
# --- Update Profile Serializer
# ----------------------------
# --------------=============--------------=============--------------=============--------------=============
class ProfileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    email = serializers.CharField(required=True) # NOTE - don't set write_only=True
    phone_number = serializers.CharField(required=True) # NOTE - don't set write_only=True
    username = serializers.CharField(required=True) # NOTE - don't set write_only=True
    first_name = serializers.CharField(required=True) # NOTE - don't set write_only=True
    last_name = serializers.CharField(required=True) # NOTE
    user_ssid = serializers.CharField(required=True) # NOTE

    
    def create(self, validated_data):
        found_existing_email = False
        find_user = User.objects.filter(id=validated_data["user_id"])
        if find_user.exists():
            if validated_data["email"] != find_user.first().email: # NOTE - the user wants to update the his/her email
                find_user_with_this_email = User.objects.filter(email=validated_data["email"])
                if find_user_with_this_email.exists():
                    found_existing_email = True
                    return {"message": "Email already exists"}
            if validated_data["email"] == find_user.first().email or not found_existing_email:
                groups = ["superuser", "admin", "student", "teacher"]
                updated_row = User.objects.filter(id=validated_data["user_id"]).update(email=validated_data["email"], username=validated_data["username"], first_name=validated_data["first_name"], last_name=validated_data["last_name"])
                user = User.objects.get(id=validated_data["user_id"])
                user_group = find_user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                user_ssid = USSID.objects.filter(user_id=user.id)
                if user_group.first().name != "superuser":
                    if user_ssid.exists():
                        user_ssid.update(ssid=validated_data["user_ssid"])
                    if not user_ssid.exists():
                        USSID.objects.create(user_id=user.id, ssid=validated_data["user_ssid"])
                    otp_model = OTPModel.objects.filter(user_id=user.id).update(receptor=validated_data["phone_number"])
                    profile_updater = ProfileUpdater.objects.get(user_id=user.id)
                    if profile_updater.update_counter == 1: # NOTE - check that the updater counter after update is 1 if so means that the user is his/her first time updates his info  
                        find_user_points = Point.objects.filter(user_id=user.id)
                        user_points = find_user_points.first().points
                        user_points += 5 # NOTE - increase 5 points on first step profile completion
                        find_user_points.update(points=user_points)
                    profile_updater.update_counter+=1
                    profile_updater.save()
                    ProfileUpdater.objects.filter(user_id=user.id).update(update_counter=profile_updater.update_counter)
                updated = {"user_id": validated_data["user_id"], "email": validated_data["email"], 
                           "phone_number": validated_data["phone_number"], "username": validated_data["username"],
                           "first_name": validated_data["first_name"], "last_name": validated_data["last_name"], "user_ssid": validated_data["user_ssid"]}
                return {"message": "Updated successfully", "data": updated}
        else:
            return {"message": "No user found"}
# --------------=============--------------=============--------------=============--------------=============


# ------------------------------
# --- Googler Register Handler
# ------------------------------
# --------------=============--------------=============--------------=============--------------=============
class GoogleAuthSerializer(serializers.Serializer):
    
    email = serializers.CharField(required=True) # NOTE - don't set write_only=True
    google_id = serializers.CharField(required=True) # NOTE - don't set write_only=True
    image_url = serializers.CharField(required=True) # NOTE - don't set write_only=True
    username = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def create(self, validated_data):
        find_user = User.objects.filter(username=validated_data['username'], email=validated_data['email'])
        if find_user.exists():
            data = {"user_id": find_user.first().id, "username": find_user.first().username}
            return {"message": "Signined successfully", "data": data}
        else:
            new_user = User.objects.create(username=validated_data['username'], email=validated_data['email'])
            user_metadata = GoogleMetaData.objects.create(user_id=new_user.id, email=validated_data['email'], google_id=validated_data['google_id'], image_url=validated_data['image_url'])
            new_group, created = Group.objects.get_or_create(name="student") # NOTE - default group is student
            group = new_group if new_group else created 
            group.user_set.add(new_user)
            ProfileUpdater.objects.create(user_id=new_user.id)
            Profile.objects.create(user_id=new_user.id)
            OTPModel.objects.create(user_id=new_user.id, receptor='', login_counter=1) # NOTE - creating a record in OTPModel table with empty receptor value for this user
            Point.objects.create(user_id=new_user.id, points=5) # NOTE - add 5 points on successfull signup
            data = {"user_id": new_user.id, "username": new_user.username}
            return {"message": "Registered successfully", "data": data}
# --------------=============--------------=============--------------=============--------------=============


# --------------------------------------------
# --- OTP Handler Request for Forgot Password
# --------------------------------------------
# --------------=============--------------=============--------------=============--------------=============
class SendOTPForgotPasswordSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def create(self, validated_data):
        
        find_otp = OTPModel.objects.filter(receptor=validated_data["phone_number"], login_counter__gt=0).exists() # NOTE - an opt model info must be exists with a login counter greater than 0
        if not find_otp:
            return {"message": "User not registered, please register"}
        else:
            find_otp = OTPModel.objects.get(receptor=validated_data["phone_number"], login_counter__gt=0) # NOTE - find an otp mode info where its login_counter field is greater than 0
            # ----------------------------
            # generating sms code
            # ----------------------------
            generated_code = random.randint(10000, 99999)
            otp_api_token = settings.SMS_API_TOKEN
            sender_number = str(settings.OTP_FIRST_SENDER_NUMBER)
            sender_second_number = str(settings.OTP_SECOND_SENDER_NUMBER)
            receiver_number = validated_data['phone_number']
            url = f'https://api.kavenegar.com/v1/{otp_api_token}/verify/lookup.json?'
            params = {'receptor': receiver_number, 'token': generated_code, 'template': "Verify"}
            sms_response = requests.post(url, params=params).json()['entries']
            if sms_response:
                updated_row = OTPModel.objects.filter(id=find_otp.id).update(recent_code=generated_code, updated_at=datetime.now(), otp_type=1) # NOTE - return the number of matched rows - otp_type 1 means forgot password
                otp_metadata = OTPMetaData.objects.create(otp_id=find_otp.id, receptor=sms_response[0]['receptor'], message_id=sms_response[0]['messageid'], sent_date=sms_response[0]['date'], cost=sms_response[0]['cost'], sender_number=sender_number)
                return {"message": "OTP has been sent"}
            else:
                return {"message": "OTP issue"}
# --------------=============--------------=============--------------=============--------------=============


# --------------------------------------
# --- OTP Forgot Password Serializer
# --------------------------------------
# --------------=============--------------=============--------------=============--------------=============
class OTPForgotPasswordSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(required=True) # NOTE - don't set write_only=True
    code = serializers.CharField(required=True) # NOTE - don't set write_only=True
    timestamp = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def create(self, validated_data):
        find_otp = OTPModel.objects.get(receptor=validated_data["phone_number"])
        incoming_dt = datetime.fromtimestamp(int(validated_data["timestamp"]))
        d1_ts = time.mktime(find_otp.updated_at.timetuple())
        d2_ts = time.mktime(incoming_dt.timetuple())
        td_mins = int(abs(d2_ts - d1_ts)) / 60
        current_server_timestamp_dt = datetime.fromtimestamp(time.time())
        td_curr_mins = int( time.mktime(current_server_timestamp_dt.timetuple()) - time.mktime(incoming_dt.timetuple()) ) / 60
        if td_mins > 2 or td_curr_mins > 2: # NOTE - OTP timeout
            return {"message": "OTP code has been expired"}
        else:
            if find_otp and find_otp.recent_code == validated_data['code']:
                find_otp.login_counter+=1
                OTPModel.objects.filter(id=find_otp.id).update(login_counter=find_otp.login_counter)
                user = User.objects.filter(id=find_otp.user_id)
                if user.exists():
                    if user.first().is_active:
                        user_info = user.values()[0]
                        data = {"user_id": user_info["id"], "username": user_info["username"]}
                        return {"message": "Valid OTP code for forgot password", "data": data}
                    else:
                        return {"message": "Account suspended", "data": []}
                else:
                    return {"message": "Please signup first"}
            else:
                return {"message": "Invalid OTP code for forgot password"}
# --------------=============--------------=============--------------=============--------------=============


# -----------------------------------
# --- OTP Handler Request for Signup
# -----------------------------------
# --------------=============--------------=============--------------=============--------------=============
class SendOTPSignupSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def create(self, validated_data):
        unsuccessful_login_for_current_user = False
        find_user = User.objects.filter(username=validated_data["phone_number"], is_active=True) # NOTE - finding the user first, cause we know that the username is the phone number of the registered user when he/she has signed up first
        find_otp = OTPModel.objects.filter(receptor=validated_data["phone_number"], otp_type=0) # NOTE - select an otp model object for signup and with a login counter greater than 0
        if find_user.exists():
            return {"message": "User already exists, please login"}
        if find_otp.exists():
            matched_otp_successful_login = OTPModel.objects.filter(receptor=validated_data["phone_number"], otp_type=0, login_counter__gt=0)
            matched_otp_unsuccessful_login = OTPModel.objects.filter(receptor=validated_data["phone_number"], otp_type=0, login_counter=0)
            if matched_otp_successful_login.exists():
                return {"message": "User already exists, please login"}
            if matched_otp_unsuccessful_login.exists():
                unsuccessful_login_for_current_user = True
            if unsuccessful_login_for_current_user:
                otp_info = find_otp.first()
        if not find_user.exists() or not find_otp.exists():
            find_only_phone = OTPModel.objects.filter(receptor=validated_data["phone_number"]) # NOTE - perhaps the user loggedin with google
            if find_only_phone.exists():
                find_user_google_data = GoogleMetaData.objects.filter(user_id=find_only_phone.first().user_id)
                if find_user_google_data.exists():
                    return {"message": "User already exists, please login"}
            else:
                otp_info = OTPModel.objects.create(receptor=validated_data["phone_number"], otp_type=0) # NOTE - 0 means otp_type is signup
            # ----------------------------
            # generating random code
            # ----------------------------
            generated_code = random.randint(10000, 99999)
            otp_api_token = settings.SMS_API_TOKEN
            sender_number = str(settings.OTP_FIRST_SENDER_NUMBER)
            sender_second_number = str(settings.OTP_SECOND_SENDER_NUMBER)
            receiver_number = validated_data['phone_number']
            url = f'https://api.kavenegar.com/v1/{otp_api_token}/verify/lookup.json?'
            params = {'receptor': receiver_number, 'token': generated_code, 'template': "Verify"}
            sms_response = requests.post(url, params=params).json()['entries']
            if sms_response:                
                updated_row = OTPModel.objects.filter(id=otp_info.id).update(recent_code=generated_code, updated_at=datetime.now()) # NOTE - return the number of matched rows
                otp_metadata = OTPMetaData.objects.create(otp_id=otp_info.id, receptor=sms_response[0]['receptor'], message_id=sms_response[0]['messageid'], sent_date=sms_response[0]['date'], cost=sms_response[0]['cost'], sender_number=sender_number)
                return {"message": "OTP has been sent"}
            else:
                return {"message": "OTP issue"}
# --------------=============--------------=============--------------=============--------------=============


# ------------------------
# --- OTP Signup Serializer
# ------------------------
# --------------=============--------------=============--------------=============--------------=============
class OTPSignupSerializer(serializers.Serializer):
    
    phone_number = serializers.CharField(required=True) # NOTE - don't set write_only=True
    code = serializers.CharField(required=True) # NOTE - don't set write_only=True
    password = serializers.CharField(required=True) # NOTE - don't set write_only=True
    timestamp = serializers.CharField(required=True) # NOTE - don't set write_only=True
    
    def create(self, validated_data):
        # ----------------------------
        # building new entries
        # ----------------------------
        find_otp = OTPModel.objects.filter(receptor=validated_data["phone_number"], otp_type=0, login_counter=0) # NOTE - login counter must be 0 to check otp signup code  
        if find_otp.exists():
            otp_info = find_otp.first()
            incoming_dt = datetime.fromtimestamp(int(validated_data["timestamp"]))
            d1_ts = time.mktime(otp_info.updated_at.timetuple())
            d2_ts = time.mktime(incoming_dt.timetuple())
            td_mins = int(abs(d2_ts - d1_ts)) / 60
            current_server_timestamp_dt = datetime.fromtimestamp(time.time())
            td_curr_mins = int( time.mktime(current_server_timestamp_dt.timetuple()) - time.mktime(incoming_dt.timetuple()) ) / 60
            if td_mins > 2 or td_curr_mins > 2: # NOTE - OTP timeout
                otp_info_for_update = OTPModel.objects.filter(id=otp_info.id).exists()
                if otp_info_for_update:
                    OTPModel.objects.filter(id=otp_info.id).update(login_counter=0) # NOTE - update the login counter to 0 means unsuccessful login
                    return {"message": "OTP code has been expired"}
            else:
                user_info = None
                user_point = None
                find_user = User.objects.filter(username=validated_data['phone_number'])
                if find_user.exists():
                    user_info = find_user.first()
                if not find_user.exists():
                    new_user = User.objects.create(username=validated_data['phone_number'])
                    new_user.set_password(validated_data['password'])
                    new_user.is_active = False
                    new_user.save()
                    new_point = Point.objects.create(user_id=new_user.id)
                    new_point.save()
                    profile = Profile.objects.create(user_id=new_user.id)
                    profile.save()
                    profile_updater = ProfileUpdater.objects.create(user_id=new_user.id)
                    profile_updater.save()
                    new_group, created = Group.objects.get_or_create(name="student") # NOTE - default group is student
                    group = new_group if new_group else created 
                    group.user_set.add(new_user)
                    user_info = new_user
                    user_point = new_point
                if otp_info.recent_code == validated_data['code']:
                    otp_info.login_counter+=1
                    OTPModel.objects.filter(id=otp_info.id).update(user_id=user_info.id, login_counter=otp_info.login_counter)
                    User.objects.filter(id=user_info.id).update(is_active=True) # NOTE - activate the user statusn
                    if user_point:
                        user_points_info = Point.objects.filter(user_id=user_info.id).update(points=5) # NOTE - increase 5 points on successfull signup
                    return {"message": "Valid OTP code for signup"}
                else:
                    OTPModel.objects.filter(id=otp_info.id).update(login_counter=0) # NOTE - update the login counter to 0 means unsuccessful login
                    return {"message": "Invalid OTP code for signup"}
        else:
            return {"message": "Something went wrong, user not found"}
# --------------=============--------------=============--------------=============--------------=============