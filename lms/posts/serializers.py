from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from comments.models import Comment
from comments.serializers import CommentListSerializer, CommentSerializer
from .models import CkeditorImage, CkeditorVideo, Post
from django.utils.text import slugify
from users.models import GoogleMetaData, Profile



class PostViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'

        
    def validate(self, attrs):
        slug_for_this_entry = slugify(attrs["title"], allow_unicode=True)
        if Post.objects.filter(slug=slug_for_this_entry).exists():
            raise serializers.ValidationError({"message": "the slug for this title already exists", "data": []})
        return attrs


class PostSerializer(serializers.ModelSerializer):
    comments = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'user_id',
            'owner_name',
            'comments',
            'visit_count',
            'slug',
        ]


    def get_comments(self, obj):
        comment_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentListSerializer(comment_qs, many=True).data
        # comments = CommentListSerializer(context={'request': comment_qs}, many=True).data
        return comments # NOTE - it'll return all published comments

    
    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            "Uknown" # NOTE - not registered user

    def get_owner_image(self, obj):
        profile_info = Profile.objects.filter(user_id=obj.user_id)
        final_image_url = ""
        if profile_info.exists():
            profile_image = profile_info.first().image
            if profile_image:
                final_image_url = profile_image.url
        google_image = GoogleMetaData.objects.filter(user_id=obj.user_id)
        if google_image.exists():
            google_image_url = google_image.first().image_url
            if google_image_url:
                final_image_url = google_image.first().image_url
        return str(final_image_url)


class PostEditSerializer(serializers.ModelSerializer):
    comments = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = [
            'user_id',
            'owner_name',
            'comments',
            'visit_count',
            'status',
            'slug',

        ]
    
    
    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            "Uknown" # NOTE - not registered user

    def get_comments(self, obj):
        comment_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentSerializer(comment_qs, many=True).data
        return comments

    def get_owner_image(self, obj):
        profile_info = Profile.objects.filter(user_id=obj.user_id)
        final_image_url = ""
        if profile_info.exists():
            profile_image = profile_info.first().image
            if profile_image:
                final_image_url = profile_image.url
        google_image = GoogleMetaData.objects.filter(user_id=obj.user_id)
        if google_image.exists():
            google_image_url = google_image.first().image_url
            if google_image_url:
                final_image_url = google_image.first().image_url
        return str(final_image_url)


class PostStatusSerializer(serializers.ModelSerializer):
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'user_id',
            'owner_name',
            'owner_image',
            'short_description',
            'content',
            'image',
            'status',
            'slug',
            'visit_count',
            'publish_time',
            'last_publish_time',
        ]
        read_only_fields = [
            'id',
            'title',
            'user_id',
            'owner_name',
            'short_description',
            'content',
            'slug',
            'visit_count',
            'publish_time',
            'last_publish_time',
        ]

    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            "Uknown" # NOTE - not registered user
            
    def get_owner_image(self, obj):
        profile_info = Profile.objects.filter(user_id=obj.user_id)
        final_image_url = ""
        if profile_info.exists():
            profile_image = profile_info.first().image
            if profile_image:
                final_image_url = profile_image.url
        google_image = GoogleMetaData.objects.filter(user_id=obj.user_id)
        if google_image.exists():
            google_image_url = google_image.first().image_url
            if google_image_url:
                final_image_url = google_image.first().image_url
        return str(final_image_url)
            
            
            
            
# ----------------------------------------
# --- Upload Image Serializer for CKeditor
# ----------------------------------------
# --------------=============--------------=============--------------=============--------------=============
class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = CkeditorImage
        fields = ["image"]    

    def create(self, validated_data):
        ck_vid = CkeditorImage.objects.create(image=validated_data["image"])
        ck_vid_info = {"image_name": ck_vid.image.name, "image_path": ck_vid.image.path, "image_url": ck_vid.image.url}
        return {'message': "Uploaded successfully", "data": ck_vid_info}
# --------------=============--------------=============--------------=============--------------=============




# ----------------------------------------
# --- Upload Video Serializer for CKeditor
# ----------------------------------------
# --------------=============--------------=============--------------=============--------------=============
class VideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=True)
    
    class Meta:
        model = CkeditorVideo
        fields = ["video"]    

    def create(self, validated_data):
        ck_vid = CkeditorVideo.objects.create(video=validated_data["video"])
        ck_img_info = {"video_name": ck_vid.video.name, "video_path": ck_vid.video.path, "video_url": ck_vid.video.url}
        return {'message': "Uploaded successfully", "data": ck_img_info}
# --------------=============--------------=============--------------=============--------------=============
