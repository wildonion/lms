

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from certificates.models import Certificate
from courses.models import User_Course
from courses.models import Course
from django.contrib.auth.models import User
from courses.serializers import CertCourseInfoSerializer
from users.models import OTPModel, USSID



class CertificateSerializer(serializers.ModelSerializer):
    
    course_info = SerializerMethodField()
    user_first_name = SerializerMethodField()
    user_last_name = SerializerMethodField()
    user_phone_number = SerializerMethodField()
    user_ssid = SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = '__all__'
        # read_only_fields = ['issued_at']
        
    def get_course_info(self, obj):
        find_user_couse = User_Course.objects.filter(id=obj.user_course_id.id)
        if find_user_couse.exists():
            course_id = find_user_couse.first().course_id
            find_course = Course.objects.filter(id=course_id)
            if find_course.exists():
                serializer = CertCourseInfoSerializer(instance=find_course.first())
                return serializer.data
            else:
                return []
        else:
            return
        
    def get_user_first_name(self, obj):
        find_user_couse = User_Course.objects.filter(id=obj.user_course_id.id)
        if find_user_couse.exists():
            user_id = find_user_couse.first().user_id
            find_user = User.objects.filter(id=user_id)
            if find_user.exists():
                return find_user.first().first_name
        else:
            return
        
    def get_user_last_name(self, obj):
        find_user_couse = User_Course.objects.filter(id=obj.user_course_id.id)
        if find_user_couse.exists():
            user_id = find_user_couse.first().user_id
            find_user = User.objects.filter(id=user_id)
            if find_user.exists():
                return find_user.first().last_name
        else:
            return
    
    def get_user_phone_number(self, obj):
        find_user_couse = User_Course.objects.filter(id=obj.user_course_id.id)
        if find_user_couse.exists():
            user_id = find_user_couse.first().user_id
            find_user_otp = OTPModel.objects.filter(user_id=user_id)
            if find_user_otp.exists():
                return find_user_otp.first().receptor
        else:
            return
    
    def get_user_ssid(self, obj):
        find_user_couse = User_Course.objects.filter(id=obj.user_course_id.id)
        if find_user_couse.exists():
            user_id = find_user_couse.first().user_id
            find_user_ssid = USSID.objects.filter(user_id=user_id)
            if find_user_ssid.exists():
                return find_user_ssid.first().ssid
        else:
            return
