

import json
from multiprocessing import managers
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from comments.models import Comment
from comments.serializers import CommentSerializer
# from courses.views import VideoListView
from users.models import GoogleMetaData, OTPModel, Point, Profile
from quizzes.models import Quizz
from products.models import Product, Discount
from tickets.models import Ticket
from tickets.serializers import TicketSerializer
from .models import Course, User_Video, Video, User_Course, Prerequisite
from django.utils.text import slugify
import subprocess
from django.contrib.auth.models import User




class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        # fields = ['id', 'title', 'short_description', 'content', 'image', 'level', 'status', 'tags']
        read_only_fields = ['created_at', 'teacher_id', 'slug', 'status', ]
        
        
    def validate(self, attrs):
        slug_for_this_entry = slugify(attrs["title"], allow_unicode=True)
        if Course.objects.filter(slug=slug_for_this_entry).exists():
            raise serializers.ValidationError({"message": "the slug for this title already exists", "data": []})
        return attrs



class CourseViewSerializer(serializers.ModelSerializer):
    # url = HyperlinkedIdentityField(
    #     view_name='course-api:listcreate',
    #     lookup_field='slug'
    # )
    
    # tags = SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        # fields = ['id', 'title', 'short_description', 'slug', ]
        
    
    # def get_tags(self, obj):
    #     return obj.tags.all().values()



class CourseEditSerializer(serializers.ModelSerializer):
    prerequisite = SerializerMethodField()
    comments = SerializerMethodField()
    tickets = SerializerMethodField()
    video_count = SerializerMethodField()
    course_duration = SerializerMethodField()
    # discounts = SerializerMethodField()
    product = SerializerMethodField()
    # tags = SerializerMethodField()
    quizzes = SerializerMethodField()
    user_course = SerializerMethodField()
    price = SerializerMethodField()
    teacher_first_name = SerializerMethodField()
    teacher_last_name = SerializerMethodField()
    teacher_avatar = SerializerMethodField()

    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'teacher_first_name',
            'teacher_last_name',
            'teacher_avatar',
            'created_at',
            'slug',
            'quizzes',
            'user_course',
            'teacher_id',
            'product',
            'price',
            # 'discounts',
            'video_count',
            'course_duration',
            'visit_count',
            'status',
            'level',
            'tags',
            'comments',
            'tickets',
            'prerequisite',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            'video_count',
            'comments',

        ]

    
    def get_teacher_first_name(self, obj):
        find_user = User.objects.filter(id=obj.teacher_id)
        if find_user.exists():
            return find_user.first().first_name
    
    
    def get_teacher_last_name(self, obj):
        find_user = User.objects.filter(id=obj.teacher_id)
        if find_user.exists():
            return find_user.first().last_name
        
    def get_teacher_avatar(self, obj):
        find_user = User.objects.filter(id=obj.teacher_id)
        final_image_url = ""
        if find_user.exists():
            profile_info = Profile.objects.filter(user_id=obj.teacher_id)
            if profile_info.exists():
                profile_image = profile_info.first().image
                if profile_image:
                    final_image_url = profile_image.url
            google_image = GoogleMetaData.objects.filter(user_id=obj.teacher_id)
            if google_image.exists():
                google_image_url = google_image.first().image_url
                if google_image_url:
                    final_image_url = google_image.first().image_url
        return final_image_url
            
    
    # def get_tags(self, obj):
    #     return obj.tags.all().values()
    
    
    def get_user_course(self, obj):
        user_courses = User_Course.objects.filter(course_id=obj.id)
        if user_courses.exists():
            return user_courses.all().values()
        else:
            return []
        
        
    def get_quizzes(self, obj):
        quizzes = Quizz.objects.filter(course_id=obj.id)
        if quizzes.exists():
            return quizzes.values('id', 'title')
        else:
            return []
        
        
    def get_video_count(self, obj):
        qs = Video.objects.filter(course_id=obj.id)
        if qs.exists():
            obj.video_count = qs.count()
            obj.save()
            return qs.count()
        else:
            return 0

    def get_course_duration(self, obj):
        course_videos_durations = list(Video.objects.filter(course_id=obj.id).values('video_duration').all())
        course_duration = 0
        v = len(course_videos_durations)
        if course_videos_durations:
            for i in range(v):
                course_duration+=course_videos_durations[i]['video_duration']
            return course_duration
        else:
            return 0

    # def get_course_duration(self, obj):
    #     qs = Video.objects.filter(course_id=obj.id)
    #     if qs.exists():
    #         courseDuration = 0
    #         for item in qs:
    #             video_path = item.clip.path
    #             duration = subprocess.run([f"ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {video_path}"], 
    #                                       shell=True,
    #                                       stdout=subprocess.PIPE, 
    #                                       stderr=subprocess.STDOUT)
    #             courseDuration += float(duration.stdout)
    #         return courseDuration
    #     else:
    #         return 0


    def get_comments(self, obj):
        c_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentSerializer(c_qs, many=True).data
        return comments

    def get_tickets(self, obj):
        t_qs = Ticket.objects.filter_by_instance(obj)
        tickets = TicketSerializer(t_qs, many=True).data
        return tickets
    
    def get_prerequisite(self, obj):
        p_qs = Prerequisite.objects.filter(main_course=obj.id)
        if p_qs.exists():
            prerequisite = PrerequisiteFetchSerializer(p_qs, many=True).data
            return prerequisite
        else:
            return []

    # def get_discounts(self, obj):
    #     all_discounts = None
    #     product = Product.objects.filter(course=obj)
    #     if product.exists():
    #         discounts = Discount.objects.filter(product=product.first(), is_expired=0, user_id=0).order_by('created_at').reverse() # NOTE - get all discounts for this product which are none expired and none belonged to any user order by their creation
    #         if discounts.exists():
    #             all_discounts = discounts.all().values('id', 'OffPercentage', 'created_at')
    #         else:
    #             all_discounts = []
    #     else:
    #         all_discounts = []
    #     return all_discounts

    def get_product(self, obj):
        product = Product.objects.filter(course_id=obj.id)
        if product.exists():
            return product.first().id # NOTE - we must only return the id of all discounts related to this course cause get discount api is restricted to only superuser group
        else:
            return []
        
    def get_price(self, obj):
        product = Product.objects.filter(course_id=obj.id)
        if product.exists():
            return product.first().price # NOTE - we must only return the id of all discounts related to this course cause get discount api is restricted to only superuser group
        else:
            return []
        


class QuizCourseInfoSerializer(serializers.ModelSerializer):
    video_count = SerializerMethodField()
    course_duration = SerializerMethodField()


    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'created_at',
            'slug',
            'teacher_id',
            'video_count',
            'course_duration',
            'visit_count',
            'status',
            'level',
            'tags',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            'video_count',
            'comments',

        ]

    def get_course_duration(self, obj):
        videos_of_course = list(Video.objects.filter(course_id=obj.id).values('video_duration').all())
        course_d = 0
        v = len(videos_of_course)
        if videos_of_course:
            for i in range(v):
                course_d+=videos_of_course[i]['video_duration']
                return course_d
        else:
            return 0
        
    def get_video_count(self, obj):
        qs = Video.objects.filter(course_id=obj.id)
        if qs.exists():
            obj.video_count = qs.count()
            obj.save()
            return qs.count()
        else:
            return 0
        
    # def get_course_duration(self, obj):
    #     qs = Video.objects.filter(course_id=obj.id)
    #     if qs.exists():
    #         courseDuration = 0
    #         for item in qs:
    #             video_path = item.clip.path
    #             duration = subprocess.run([f"ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {video_path}"], 
    #                                       shell=True,
    #                                       stdout=subprocess.PIPE, 
    #                                       stderr=subprocess.STDOUT)
    #             courseDuration += float(duration.stdout)
    #         return courseDuration
    #     else:
    #         return 0
        
        

class CertCourseInfoSerializer(serializers.ModelSerializer):

    user_course = SerializerMethodField()
    price = SerializerMethodField()
    
    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'price',
            'created_at',
            'slug',
            'user_course',
            'teacher_id',
            'visit_count',
            'status',
            'level',
            'tags',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            'video_count',
            'comments',

        ]
        
    def get_user_course(self, obj):
        user_courses = User_Course.objects.filter(course_id=obj.id)
        if user_courses.exists():
            return user_courses.all().values()
        else:
            return []
    
    def get_price(self, obj):
        product = Product.objects.filter(course_id=obj.id)
        if product.exists():
            return product.first().price # NOTE - we must only return the id of all discounts related to this course cause get discount api is restricted to only superuser group
        else:
            return []


class ProdLoadMoreCourseInfoSerializer(serializers.ModelSerializer):
    
    prerequisite = SerializerMethodField()
    user_course = SerializerMethodField()
    video_count = SerializerMethodField()
    
    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'prerequisite',
            'content',
            'image',
            'user_course',
            'created_at',
            'slug',
            'video_count',
            'visit_count',
            'status',
            'level',
            'tags',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            # 'video_count',
            'comments',

        ]
    
    def get_prerequisite(self, obj):
        p_qs = Prerequisite.objects.filter(main_course=obj.id)
        if p_qs.exists():
            prerequisite = PrerequisiteFetchSerializer(p_qs, many=True).data
            return prerequisite
        else:
            return []
    
    
    def get_user_course(self, obj):
        user_courses = User_Course.objects.filter(course_id=obj.id)
        if user_courses.exists():
            return user_courses.all().values()
        else:
            return []
    
    def get_video_count(self, obj):
        qs = Video.objects.filter(course_id=obj.id)
        if qs.exists():
            obj.video_count = qs.count()
            obj.save()
            return qs.count()
        else:
            return 0
        


class ProdCourseInfoSerializer(serializers.ModelSerializer):
    
    user_course = SerializerMethodField()
    prerequisite = SerializerMethodField()
    
    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'prerequisite',
            'content',
            'image',
            'created_at',
            'user_course',
            'slug',
            'teacher_id',
            'visit_count',
            'status',
            'level',
            'tags',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            'video_count',
            'comments',

        ]
        
    def get_prerequisite(self, obj):
        p_qs = Prerequisite.objects.filter(main_course=obj.id)
        if p_qs.exists():
            prerequisite = PrerequisiteFetchSerializer(p_qs, many=True).data
            return prerequisite
        else:
            return []
    
    def get_user_course(self, obj):
        user_courses = User_Course.objects.filter(course_id=obj.id)
        if user_courses.exists():
            return user_courses.all().values()
        else:
            return []
        



        
class UserCourseInfoSerializer(serializers.ModelSerializer):
    video_count = SerializerMethodField()
    course_duration = SerializerMethodField()
    product = SerializerMethodField()
    quizzes = SerializerMethodField()
    teacher_first_name = SerializerMethodField()
    teacher_last_name = SerializerMethodField()

    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'created_at',
            'slug',
            'quizzes',
            'teacher_id',
            'teacher_first_name',
            'teacher_last_name',
            'product',
            'video_count',
            'course_duration',
            'visit_count',
            'status',
            'level',
            'tags',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'created_at',
            'publish_time',
            'last_publish_time',
            'slug',
            'teacher_id',
            'status',
            'visit_count',
            'video_count',
            'comments',

        ]

        
    def get_quizzes(self, obj):
        quizzes = Quizz.objects.filter(course_id=obj.id)
        if quizzes.exists():
            return quizzes.values('id', 'title')
        else:
            return []
        
        
    def get_video_count(self, obj):
        qs = Video.objects.filter(course_id=obj.id)
        if qs.exists():
            obj.video_count = qs.count()
            obj.save()
            return qs.count()
        else:
            return 0
        
    # def get_course_duration(self, obj):
    #     qs = Video.objects.filter(course_id=obj.id)
    #     if qs.exists():
    #         courseDuration = 0
    #         for item in qs:
    #             video_path = item.clip.path
    #             duration = subprocess.run([f"ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 {video_path}"], 
    #                                       shell=True,
    #                                       stdout=subprocess.PIPE, 
    #                                       stderr=subprocess.STDOUT)
    #             courseDuration += float(duration.stdout)
    #         return courseDuration
    #     else:
    #         return 0

    def get_course_duration(self, obj):
        course_videos = Video.objects.filter(course_id=obj.id)
        course_duration = 0
        if course_videos.exists():
            for item in course_videos:
                serializer = VideoSerializer(instance=item)
                course_duration+=serializer.data['video_duration']
            return course_duration
        else:
            return 0

    def get_product(self, obj):
        product = Product.objects.filter(course_id=obj.id)
        if product.exists():
            return product.first().id # NOTE - we must only return the id of all discounts related to this course cause get discount api is restricted to only superuser group
        else:
            return []
        
    def get_teacher_first_name(self, obj):
        find_user = User.objects.filter(id=obj.teacher_id)
        if find_user.exists():
            return find_user.first().first_name
    
    
    def get_teacher_last_name(self, obj):
        find_user = User.objects.filter(id=obj.teacher_id)
        if find_user.exists():
            return find_user.first().last_name


class CourseChangeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        # fields = '__all__'
        fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'status',
            'publish_time',
            'last_publish_time',
            'visit_count',

        ]
        read_only_fields = [
            'id',
            'title',
            'short_description',
            'content',
            'image',
            'created_at',
            'teacher_id',
            'slug',
            'publish_time',
            'last_publish_time',
            'visit_count',

        ]



class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['video_format', 'video_size',  'created_at', 'slug']



class VideoSerializer(serializers.ModelSerializer):
    # video_duration = SerializerMethodField()
    course_info = SerializerMethodField()

    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['video_format', 'video_size', 'video_duration', 'image', 'created_at', 'slug']

    def get_course_info(self, obj):
        print(obj)
        find_course = Course.objects.filter(id=obj.course_id)
        if find_course.exists():
            serializer = CourseEditSerializer(instance=find_course.first())
            return serializer.data
        else:
            return []
        


class User_VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_Video
        fields = '__all__'



class User_CourseSerializer(serializers.ModelSerializer):
    course_info = SerializerMethodField()
    
    class Meta:
        model = User_Course
        fields = '__all__'
        
        
    def get_course_info(self, obj):
        find_course = Course.objects.filter(id=obj.course_id)
        if find_course.exists():
            serializer = UserCourseInfoSerializer(instance=find_course.first())
            return serializer.data
        else:
            return []

class PrerequisiteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Prerequisite
        fields = '__all__'


class PrerequisiteFetchSerializer(serializers.ModelSerializer):
    main_course = SerializerMethodField()
    prerequisite_courses = SerializerMethodField()
    
    class Meta:
        model = Prerequisite
        fields = '__all__'
        
        
    def get_main_course(self, obj):
        return Course.objects.filter(id=obj.main_course).values('id', 'slug', 'title')
    
    def get_prerequisite_courses(self, obj):
        return obj.prerequisite_courses.all().values('id', 'slug', 'title')