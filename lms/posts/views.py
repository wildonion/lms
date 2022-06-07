


from functools import reduce
from urllib import response
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.utils import timezone
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from users.utils import decode_token
from .models import Post
from .serializers import PostSerializer, PostStatusSerializer, PostEditSerializer, PostViewSerializer, ImageSerializer, VideoSerializer
from rest_framework.decorators import api_view









# ------------------------------
# --- Ckeditor Update Image
# ------------------------------
@api_view(['POST'])
def ckeditor_upload_image(request):
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
                groups = ["superuser", "admin"]
                user_group = user.first().groups.filter(
                    reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"},
                                    status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = ImageSerializer(data=request.data)
            if serializer.is_valid():
                resp = serializer.create(serializer.validated_data)
                serializer_data = serializer.data
                serializer_data["response"] = resp
                serializer_data["response"]["token_status"] = token_msg
                response.data = serializer_data["response"]
                response.status_code = HTTP_201_CREATED
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response







# ------------------------------
# --- Ckeditor Update Video
# ------------------------------
@api_view(['POST'])
def ckeditor_upload_video(request):
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
                groups = ["superuser", "admin"]
                user_group = user.first().groups.filter(
                    reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"},
                                    status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = VideoSerializer(data=request.data)
            if serializer.is_valid():
                resp = serializer.create(serializer.validated_data)
                serializer_data = serializer.data
                serializer_data["response"] = resp
                serializer_data["response"]["token_status"] = token_msg
                response.data = serializer_data["response"]
                response.status_code = HTTP_201_CREATED
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response





class PostListAPIView(ListAPIView):
    queryset = Post.published_objects.all()
    serializer_class = PostViewSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'short_description', 'content', ]

    def get(self, request, *args, **kwargs):
        response = Response()
        published_post = self.list(request, *args, **kwargs)
        if published_post.data:
            for pp in published_post.data:
                if pp["image"] != None:
                    pp["image"] = pp["image"][21:]
            response.data = {"message": "Fetched successfully", "data": published_post.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No published post found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response

class AllPostListAPIView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostViewSerializer


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
                    groups = ["superuser", "admin"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                all_posts = self.list(request, *args, **kwargs)
                for post in all_posts.data:
                    if post["image"] != None:
                        post["image"] = post["image"][21:]
                response.data = {"message": token_msg, "data": all_posts.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response













class PostEditAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostEditSerializer
    lookup_field = 'slug'

    
    
    def get(self, request, *args, **kwargs):
        response = Response()
        instance = self.get_object()
        instance.visit_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data["image"] = serializer_data["image"][21:] if serializer_data["image"] != None else ''
        response.data = {"message": "Fetched successfully", "data": serializer_data}
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
                    groups = ["admin", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                updated_post = self.partial_update(request, *args, **kwargs)
                updated_post.data["image"] = updated_post.data["image"][21:] if updated_post.data["image"] != None else ''
                response.data = {"message": token_msg, "data": updated_post.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


class PostCreateAPIView(CreateAPIView):
    queryset = Post.published_objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.data["user_id"])

    
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
                    groups = ["admin", "superuser"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists() or int(request.data["user_id"]) != user.first().id:
                        return Response({"message": f"Access denied for users with none {groups} group"}, status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                created_post = self.create(request, *args, **kwargs)
                created_post.data["image"] = created_post.data["image"][21:] if created_post.data["image"] != None else ''
                response.data = {"message": token_msg, "data": created_post.data}
                response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    
    
    
    

class PostChangeStatus(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostStatusSerializer
    lookup_field = 'slug'

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
                    groups = ["superuser", "admin"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                instance = self.get_object()
                if request.data.get("status") == 'published':
                    if instance.publish_time:
                        instance.last_publish_time = timezone.now()
                        instance.status = 'published'
                    else:
                        instance.publish_time = timezone.now()
                        instance.last_publish_time = timezone.now()
                        instance.status = 'published'
                if request.data.get("status") == 'draft':
                    instance.status = 'draft'
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                serializer_data = serializer.data
                serializer_data["image"] = serializer_data["image"][21:] if serializer_data["image"] != None else '' 
                response.status_code = HTTP_200_OK
                response.data = {"message": token_msg, "data": serializer_data}
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
    posts = Post.objects.filter(status="published")
    if len(posts) == 0:
        response.data = {"message": "No posts", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    for index, post in enumerate(posts):
        if from_number <= index:
            serializer = PostSerializer(instance=posts.all()[from_number: to_number+1], many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        if from_number > index:
            response.data = {"message": "Out of index", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
    return response

@api_view(['POST'])
def search_by_tag(request):
    response = Response()
    from_number = int(request.data['from'])
    to_number = int(request.data['to'])
    find_tag = request.data['tag']
    result = []
    published_posts = Post.objects.filter(status="published")
    for post in published_posts:
        if find_tag in post.tags:
            result.append(post)
    if len(result) == 0:
        response.data = {"message": "No posts for this tag", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    for index, post in enumerate(result):
        if from_number <= index:
            serializer = PostSerializer(instance= result[from_number:to_number+1], many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        if from_number > index:
            response.data = {"message": "Out of index", "data": []}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
    return response

@api_view(['POST'])
def post_categ(request):
    find_categ = request.data['categ']
    published_posts = Post.objects.filter(status='published')
    if published_posts.exists():
        posts = published_posts.filter(categ=find_categ)
        for post in posts.values():
            if post["image"] != None:
                post["image"] = post["image"][21:]
        serializer = PostSerializer(instance=posts, many=True)
        return Response({"message": "Fetched successfully", "data": serializer.data}, status=HTTP_200_OK)
