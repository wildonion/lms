from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer

from posts.models import Post
from .models import Comment
from users.models import GoogleMetaData, Profile





def create_comment_serializer(model_type=None, slug=None, parent_id=None, user_id=None):
    class CommentCreateSerializer(ModelSerializer):
        owner_name = SerializerMethodField()
        owner_image = SerializerMethodField()
        
        
        class Meta:
            model = Comment
            fields = [
                'id',
                'user_id',
                'owner_name',
                'owner_image',
                'content',
                'created_at',
            ]
            read_only_fields = ['user_id', ]

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(CommentCreateSerializer, self).__init__(*args, **kwargs)

        def validate(self, data):
            model_type = self.model_type
            model_qs = ContentType.objects.filter(model=model_type)
            if not model_qs.exists() or model_qs.count() != 1:
                raise ValidationError("This is not a valid content type")
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=self.slug)
            if not obj_qs.exists() or obj_qs.count() != 1:
                raise ValidationError("This is not a slug for this content type")
            return data
        
        def get_owner_name(self, obj):
            user = User.objects.filter(id=obj.user_id)
            if user.exists():
                return str(user.first().username)
            else:
                return "Uknown" # NOTE - not registered user
        
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

        def create(self, validated_data):
            content = validated_data.get('content')
            if user_id:
                main_user_id = user_id
            else:
                main_user_id = 0
            model_type = self.model_type
            slug = self.slug
            parent_obj = self.parent_obj
            comment = Comment.objects.create_by_model_type(model_type=model_type, slug=slug, content=content, user_id=main_user_id, parent_obj=parent_obj)
            return comment

    return CommentCreateSerializer



class CommentSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    owner_image = SerializerMethodField()
    owner_name = SerializerMethodField()
    post_title = SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0
    
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


    def get_owner_name(self, obj):
            user = User.objects.filter(id=obj.user_id)
            if user.exists():
                return str(user.first().username)
            else:
                return "Uknown" # NOTE - not registered user
                
    def get_post_title(self, obj):
            post = Post.objects.filter(id=obj.object_id)
            if post.exists():
                return post.first().title
            else:
                return ""


class CommentListSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()
    
    
    class Meta:
        model = Comment
        fields = '__all__'

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0

    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            return "Uknown" # NOTE - not registered user

    
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


class CommentChildSerializer(ModelSerializer):
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            return "Uknown" # NOTE - not registered user
            
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



class CommentEditSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    replies = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()


    class Meta:
        model = Comment
        fields = '__all__'

    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            return "Uknown" # NOTE - not registered user
    
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

    def get_replies(self, obj):
        if obj.is_parent:
            return CommentChildSerializer(obj.children(), many=True).data
            # in MODEL ==>  def children(self): return Comment.objects.filter(parent=self)
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0
    
    
    
class CommentChangeStatusSerializer(ModelSerializer):
    
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()
    
    
    class Meta:
        model = Comment
        fields = '__all__'
        
    
    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            return "Uknown" # NOTE - not registered user
    
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