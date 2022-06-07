




from numpy import product
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from products.models import Product
from products.serializers import ProductSerializer
from .models import PaymentInfo
from django.contrib.auth.models import User
from users.models import OTPModel



class PaymentInfoSerializer(serializers.ModelSerializer):
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()
    user_phone_number = SerializerMethodField()
    product_info = SerializerMethodField()
    
    class Meta:
        model = PaymentInfo
        fields = '__all__'
        
        
    def get_first_name(self, obj):
        find_user = User.objects.filter(id=obj.user_id)
        if find_user.exists():
            return find_user.first().first_name
    
    
    def get_last_name(self, obj):
        find_user = User.objects.filter(id=obj.user_id)
        if find_user.exists():
            return find_user.first().last_name
        
    
    def get_user_phone_number(self, obj):
        find_user_otp = OTPModel.objects.filter(user_id=obj.user_id)
        if find_user_otp.exists():
            return find_user_otp.first().receptor
    
    def get_product_info(self, obj):
        find_product = Product.objects.filter(id=obj.product_id)
        if find_product.exists():
            prod = find_product.first()
            serializer = ProductSerializer(instance=prod)
            return serializer.data