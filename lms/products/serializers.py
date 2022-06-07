from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from courses.models import Course
from courses.serializers import ProdCourseInfoSerializer, ProdLoadMoreCourseInfoSerializer

from .models import Product, Discount



class ProductSerializer(ModelSerializer):
    course_info = SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['mean_score', 'created_at', 'last_updated_at', ]

    def get_course_info(self, obj):
        find_course = Course.objects.filter(id=obj.course_id)
        if find_course.exists():
            serializer = ProdLoadMoreCourseInfoSerializer(instance=find_course.first())
            return serializer.data
        else:
            return []



class ProductEditSerializer(ModelSerializer):
    course_info = SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = [
            'course_id',
            'created_at',
            'last_updated_at',
        ]

    def get_course_info(self, obj):
        find_course = Course.objects.filter(id=obj.course_id)
        if find_course.exists():
            serializer = ProdCourseInfoSerializer(instance=find_course.first())
            return serializer.data
        else:
            return []



class DiscountSerializer(ModelSerializer):

    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
        ]



class DiscountEditSerializer(ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
            'product',
        ]
