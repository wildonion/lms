from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from users.models import Profile
from .models import Ticket




def create_Ticket_serializer(model_type=None, slug=None, parent_id=None, user_id=None):
    class TicketCreateSerializer(ModelSerializer):
        owner_name = SerializerMethodField()
        owner_image = SerializerMethodField()
        
        
        class Meta:
            model = Ticket
            fields = [
                'id',
                'user_id',
                'owner_name',
                'content',
                'created_at',
            ]
            read_only_fields = ['user_id', ]

        def __init__(self, *args, **kwargs):
            self.model_type = model_type
            self.slug = slug
            self.parent_obj = None
            if parent_id:
                parent_qs = Ticket.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    self.parent_obj = parent_qs.first()
            return super(TicketCreateSerializer, self).__init__(*args, **kwargs)

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
                "Uknown" # NOTE - not registered user
                
        def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user

        def create(self, validated_data):
            content = validated_data.get('content')
            if user_id:
                main_user_id = user_id
            else:
                main_user_id = 0
            model_type = self.model_type
            slug = self.slug
            parent_obj = self.parent_obj
            ticket = Ticket.objects.create_by_model_type(model_type=model_type, slug=slug, content=content, user_id=main_user_id, parent_obj=parent_obj)
            return ticket

    return TicketCreateSerializer


class TicketSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    owner_image = SerializerMethodField()
    owner_name = SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0
    
    def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user
                
    def get_owner_name(self, obj):
            user = User.objects.filter(id=obj.user_id)
            if user.exists():
                return str(user.first().username)
            else:
                "Uknown" # NOTE - not registered user


class TicketListSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()


    class Meta:
        model = Ticket
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
            "Uknown" # NOTE - not registered user
            
    def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user


class TicketChildSerializer(ModelSerializer):
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_owner_name(self, obj):
        return str(obj.owner.username)
    
    def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user


class TicketEditSerializer(ModelSerializer):
    reply_count = SerializerMethodField()
    replies = SerializerMethodField()
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'


    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            "Uknown" # NOTE - not registered user

    def get_replies(self, obj):
        if obj.is_parent:
            return TicketChildSerializer(obj.children(), many=True).data
            # in MODEL ==>  def children(self): return Ticket.objects.filter(parent=self)
        return None

    def get_reply_count(self, obj):
        if obj.is_parent:
            return obj.children().count()
        return 0

    
    def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user

class TicketChangeStatusSerializer(ModelSerializer):
    owner_name = SerializerMethodField()
    owner_image = SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = '__all__'

    def get_owner_image(self, obj):
            find_user_image = Profile.objects.filter(user_id=obj.user_id)
            if find_user_image.exists():
                user_image = find_user_image.first().image.url
                return str(user_image)
            else:
                "Uknown" # NOTE - not registered user
                
    def get_owner_name(self, obj):
        user = User.objects.filter(id=obj.user_id)
        if user.exists():
            return str(user.first().username)
        else:
            "Uknown" # NOTE - not registered user