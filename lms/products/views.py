


from functools import reduce
import re
import string
from urllib import response
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from django.utils import timezone
from courses.models import Course
from users.utils import decode_token
from django.conf import settings
from .models import Product, Discount
from .serializers import ProductSerializer, ProductEditSerializer, DiscountSerializer, DiscountEditSerializer
from . import utils
from users.models import Point
from rest_framework.decorators import api_view



class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    def post(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                find_product = Product.objects.filter(course_id=request.data["course"])
                if find_product.exists():
                    response.data = {"message": token_msg, "data": find_product.all().values()}
                    response.status_code = HTTP_302_FOUND    
                else:
                    created_product = self.create(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": created_product.data}
                    response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response




class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    def get(self, request, *args, **kwargs):
        response = Response()
        published_courses = list(Course.objects.filter(status='published').all().values('id'))
        find_published_courses_products = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in published_courses]))
        if find_published_courses_products.exists():
            serializer = ProductSerializer(instance=find_published_courses_products, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No products found", "data": []} # NOTE - perhaps there are no published course
            response.status_code = HTTP_404_NOT_FOUND
        return response
    
    
    


class ProductRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductEditSerializer
    lookup_field = 'pk'
    
    def get(self, request, *args, **kwargs):
        response = Response()
        product_detail = self.retrieve(request, *args, **kwargs)
        response.data = {"message": "Fetched successfully", "data": product_detail.data}
        response.status_code = HTTP_200_OK
        return response
    

    def patch(self, request, *args, **kwargs):    
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                if user_group.first().name == "student":
                    mean_score = int(request.data["mean_score"]) if "mean_score" in request.data else 0
                    mean_score /= 10 # NOTE - will be in range between 0 up to 5  
                    find_product = Product.objects.filter(id=self.kwargs.get("pk"))
                    if find_product.exists():
                        last_mean_score = float(find_product.first().mean_score/10)
                        last_mean_score_counter = find_product.first().mean_score_counter
                        if last_mean_score_counter == 0:
                            updated_mean_score = mean_score * 10
                        else:
                            updated_mean_score = int((last_mean_score + mean_score) / 2) * 10
                        last_mean_score_counter+=1
                        find_product.update(mean_score_counter=last_mean_score_counter, mean_score=updated_mean_score)
                        data = {"id": self.kwargs.get("pk"), "mean_score": updated_mean_score}
                        response.data = {"message": token_msg, "data": data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                if user_group.first().name == "superuser":
                    updated_product = self.partial_update(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": updated_product.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response














class DiscountCreateView(generics.CreateAPIView):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()
    
    def post(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                created_discount = self.create(request, *args, **kwargs)
                response.data = {"message": token_msg, "data": created_discount.data}
                response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    



class DiscountCreateUserView(generics.CreateAPIView): # NOTE - this api will be used for creating discount in user panel for staking certificates
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()
    
    def post(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                user_discount_api_key = str(settings.USER_DISCOUNT_API_KEY)
                if request.data["user_discount_api_key"] != "" and request.data["user_discount_api_key"] == user_discount_api_key:
                    created_discount = self.create(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": created_discount.data}
                    response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    



class CheckDiscount(generics.ListAPIView):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()
    
    def post(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                find_product_discounts_for_this_user = Discount.objects.filter(code=request.data["code"])
                if find_product_discounts_for_this_user.exists():
                    if find_product_discounts_for_this_user.first().is_expired == 1:
                        response.data = {"message": token_msg, "error": "Discount code has been expired"}
                        response.status_code = HTTP_404_NOT_FOUND
                        return response
                    if find_product_discounts_for_this_user.first().status == "unique" and find_product_discounts_for_this_user.first().product_id == 0: # NOTE - means this code has been generated for users
                        data = {"discount_id": find_product_discounts_for_this_user.first().id, "product_id": find_product_discounts_for_this_user.first().product_id, "status": find_product_discounts_for_this_user.first().status, "is_expired": 0 , "offpercentage": find_product_discounts_for_this_user.first().offpercentage}
                        response.data = {"message": token_msg, "data": data}
                        response.status_code = HTTP_200_OK
                        return response
                    if find_product_discounts_for_this_user.first().status == "general" and find_product_discounts_for_this_user.first().product_id != 0: # NOTE - means this code has been generated for a specific product
                        data = {"discount_id": find_product_discounts_for_this_user.first().id, "product_id": find_product_discounts_for_this_user.first().product_id, "status": find_product_discounts_for_this_user.first().status, "is_expired": 0, "offpercentage": find_product_discounts_for_this_user.first().offpercentage} # NOTE - we won't set is_expired to 1 cause superuser must update it inside the panel manually 
                        response.data = {"message": token_msg, "data": data}
                        response.status_code = HTTP_200_OK
                        return response
                else:
                    response.data = {"message": token_msg, "error": "Wrong discount code"}
                    response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


class DiscountListView(generics.ListAPIView):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()
    
    def post(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                all_discounts_for_superuser = False if "product_id" in request.data else True
                if all_discounts_for_superuser:
                    discounts = self.list(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": discounts.data}
                    response.status_code = HTTP_200_OK
                else:
                    find_product_discounts = Discount.objects.filter(product=request.data["product_id"], is_expired=0, user_id=0) # NOTE - get all discounts for this product which are none expired and none belonged to any user order by their creation
                    if find_product_discounts.exists():
                        serializer = DiscountSerializer(instance=find_product_discounts, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


class DiscountRetrieveUpdateView(RetrieveUpdateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountEditSerializer

    def get(self, request, *args, **kwargs):
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                discount_detail = self.retrieve(request, *args, **kwargs)
                response.data = {"message": token_msg, "data": discount_detail.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    
    def patch(self, request, *args, **kwargs):    
        response = Response()
        if 'Authorization' in request.headers:
            token = request.headers.get("Authorization")[7:]
            payload = decode_token(token)
            if payload == "decode error":
                response.data = {'message': "Can't decode jwt"}
                response.status_code = HTTP_406_NOT_ACCEPTABLE
            elif payload == "expired":
                response.data = {'message': "Token has been expired"}
                response.status_code = HTTP_401_UNAUTHORIZED
            else:
                user = User.objects.filter(id=payload["user_id"])
                if user.exists():
                    token_msg = "Valid token"
                    groups = ["superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                # if user_group.first().name == "student":
                #     user_id = user.first().id
                #     minimum_points_required_for_discount = int(settings.MINIMUM_POINT_AMOUNTS_FOR_DISCOUNT_CODE)
                #     decreas_points_amount = int(settings.DECREASE_POINT_AMOUNTS_FOR_DISCOUNT_CODE)
                #     expiration_time = int(settings.EXPIRATION_TIME_FOR_USER_DISCOUNT_CODE_BASED_ON_POINTS) # TODO - based on day
                #     find_user_point = Point.objects.filter(user_id=user_id)
                #     if find_user_point.exists():
                #         user_points = find_user_point.first().points
                #         if user_points >= minimum_points_required_for_discount:
                #             discount_code = utils.discount_generator()
                #             find_user_discount = Discount.objects.filter(user_id=user_id, id=self.kwargs.get("pk"))
                #             if find_user_discount.exists():
                #                 find_user_discount.update(code=discount_code)
                #                 user_points -= decreas_points_amount
                #                 find_user_point.update(points=user_points)
                #                 response.data = {"message": "Updated successfully" , "data": {"user_points": user_points}}
                #                 response.status_code = HTTP_200_OK
                #             else:
                #                 Discount.objects.create(user_id=user_id, code=discount_code)
                #                 user_points -= decreas_points_amount
                #                 find_user_point.update(points=user_points)
                #                 response.data = {"message": "Created successfully" , "data": {"user_points": user_points}}
                #                 response.status_code = HTTP_200_OK
                #         else:
                #             response.data = {"message": "Not enough points", "data": []}
                #             response.status_code = HTTP_406_NOT_ACCEPTABLE
                if user_group.first().name == "superuser":
                    # TODO - if a none user discount code was generated with an expiration time for a product we can't generate a new one for that product unless the old one expires
                    # TODO - expiration time for generated none user discount code
                    # TODO - expire discount codes after a specific time - update is_expired field to 1
                    # ...
                    expiration_time = int(settings.EXPIRATION_TIME_FOR_USER_DISCOUNT_CODE_GENERATED_BY_SUPERUSER) # NOTE - based on day
                    updated_discount = self.partial_update(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": updated_discount.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response

@api_view(['POST'])
def load_more(request):
    response = Response()
    from_number = int(request.data['from'])
    to_number = int(request.data['to'])
    published_courses = list(Course.objects.filter(status='published').all().values('id'))
    find_published_courses_products = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in published_courses]))
    if len(find_published_courses_products) == 0:
        response.data = {"message": "No product", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    for index, product in enumerate(find_published_courses_products):
        if from_number <= index:
            serializer = ProductSerializer(instance= find_published_courses_products[from_number:to_number+1], many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        if from_number > index:
            response.data = {"message": "Out of index", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
    return response

@api_view(['POST'])
def load_course_by_level(request):
    response = Response()
    level = request.data['level']
    capsed_level = string.capwords(level)
    published_courses_requested_level = Course.objects.filter(status='published', level = capsed_level).all().values('id')
    if published_courses_requested_level.exists():
        find_published_courses_products = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in published_courses_requested_level]))
        if find_published_courses_products.exists() & len(find_published_courses_products) >= 5:
            courses = find_published_courses_products[:5]
            serializer = ProductSerializer(instance= courses, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        if find_published_courses_products.exists() & 0< len(find_published_courses_products) < 5:
            courses = find_published_courses_products
            serializer = ProductSerializer(instance= courses, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
        else:
            response.data = {"message": "No product", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
    else:
        response.data = {"message": "No product", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    return response

@api_view(['GET'])
def load_quiz(request):
    response = Response()
    published_courses_no_video = Course.objects.filter(status='published', video_count=0).all().values('id')
    if published_courses_no_video.exists():
        published_courses_no_video_product = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in published_courses_no_video]))
        if published_courses_no_video_product.exists() & len(published_courses_no_video_product) >= 5:
            courses = published_courses_no_video_product[:5]
            serializer = ProductSerializer(instance= courses, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        if published_courses_no_video_product.exists() & 0 < len(published_courses_no_video_product) < 5:
            courses = published_courses_no_video_product
            serializer = ProductSerializer(instance= courses, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
        else:
            response.data = {"message": "No product", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
    else:
        response.data = {"message": "No product", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    return response

@api_view(["POST"])
def search(request):
    response = Response()
    phrase = request.data['phrase']
    published_courses = Course.objects.filter(status='published').all().values('id')
    find_published_courses_products = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in published_courses])).all().values('id')
    if find_published_courses_products.exists():
        find_phrase_in_course = Course.objects.filter(reduce(lambda x, y: x | y, [Q(title__icontains=phrase) | Q(short_description__icontains=phrase) | Q(content__icontains=phrase) for item in find_published_courses_products])).distinct().all().values('id')
        if find_phrase_in_course.exists():
            res = Product.objects.filter(reduce(lambda x, y: x | y, [Q(course_id=item['id']) for item in find_phrase_in_course]))
            if res.exists():
                serializer = ProductSerializer(instance= res, many=True)
                response.data = {"message": "Fetched successfully", "data": serializer.data}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": "No product", "data": []}
                response.status_code = HTTP_404_NOT_FOUND
        else:
            response.data = {"message": "Phrase Not Found In Courses", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
    else:
        response.data = {"message": "No product", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    return response
    
@api_view(['POST'])
def expire_discount(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "student"]
                user_group = user.first().groups.filter(
                    reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for users with none {groups} group"},
                                    status=HTTP_403_FORBIDDEN)
            else:
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            discount_id = request.data["discount_id"]
            find_discount = Discount.objects.filter(id=discount_id)
            if find_discount.exists() and find_discount.first().status == "unique":
                find_discount.update(is_expired=1, updated_at=timezone.now()) # NOTE - expire discount only if for a user; we won't expire general discounts cause superuser must expire them in the panel
                serializer = DiscountSerializer(instance=find_discount, many=True)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": token_msg, "data": []}
                response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response