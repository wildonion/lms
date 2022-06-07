from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from comments.models import Comment
from comments.serializers import CommentListSerializer, CommentSerializer
from .models import CkeditorImageProp, CkeditorVideoProp, Proposal
from django.utils.text import slugify







class ProposalViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        fields = '__all__'

        
    def validate(self, attrs):
        slug_for_this_entry = slugify(attrs["title"], allow_unicode=True)
        if Proposal.objects.filter(slug=slug_for_this_entry).exists():
            raise serializers.ValidationError({"message": "the slug for this title already exists", "data": []})
        return attrs


class ProposalSerializer(serializers.ModelSerializer):
    comments = SerializerMethodField()
    owner_name = SerializerMethodField()

    class Meta:
        model = Proposal
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

class ProposalEditSerializer(serializers.ModelSerializer):
    comments = SerializerMethodField()
    owner_name = SerializerMethodField()
    # tags = SerializerMethodField()

    class Meta:
        model = Proposal
        fields = '__all__'
        read_only_fields = [
            'user_id',
            'owner_name',
            'comments',
            'visit_count',
            'status',
            'slug',

        ]


    # def get_tags(self, obj):
    #     return obj.tags.all().values()
    
    
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


class ProposalStatusSerializer(serializers.ModelSerializer):
    owner_name = SerializerMethodField()

    class Meta:
        model = Proposal
        fields = [
            'id',
            'title',
            'user_id',
            'owner_name',
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
            
            
            
            
            
            
# ----------------------------------------
# --- Upload Image Serializer for CKeditor
# ----------------------------------------
# --------------=============--------------=============--------------=============--------------=============
class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = CkeditorImageProp
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
        model = CkeditorVideoProp
        fields = ["video"]    

    def create(self, validated_data):
        ck_vid = CkeditorVideo.objects.create(video=validated_data["video"])
        ck_img_info = {"video_name": ck_vid.video.name, "video_path": ck_vid.video.path, "video_url": ck_vid.video.url}
        return {'message': "Uploaded successfully", "data": ck_img_info}
# --------------=============--------------=============--------------=============--------------=============