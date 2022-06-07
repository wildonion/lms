


from functools import reduce
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from users.utils import decode_token
from .models import Comment
from .serializers import CommentChangeStatusSerializer, CommentListSerializer, CommentSerializer, create_comment_serializer, CommentEditSerializer







# NOTE - this is the main view to create a comment and it will return an instance of the serializer
class CommentCreateAPIView(CreateAPIView):
    queryset = Comment.objects.all()
    
    def get_serializer_class(self, *args, **kwargs):
        model_type = self.request.GET.get('type')
        slug = self.request.GET.get('slug')
        parent_id = self.request.GET.get('parent_id', None)
        user_id = self.request.GET.get('user_id', None)
        comment = create_comment_serializer(model_type=model_type, slug=slug, parent_id=parent_id, user_id=user_id)
        return comment
    
    
    
    
    
# NOTE - this is the proxy view to call the main view of creating comment
class CommentCreateAPIViewPost(CreateAPIView):
    
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
                    groups = ["superuser", "admin", "student", "teacher"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            comment = CommentCreateAPIView.as_view()(self.request._request) # NOTE - calling the main view with to create the comment - self.request._request is the django http request and self.request is the django rest framework request object
            response.data = {"message": "Sent successfully", "data": comment.data}
            response.status_code = HTTP_201_CREATED
            # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response





class CommentListAPIView(ListAPIView):
    serializer_class = CommentListSerializer
    filter_backend = [SearchFilter]
    search_fields = ['content', ]

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
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                comments = Comment.objects.filter(id__gte=0)
                if comments.exists():
                    serializer = CommentSerializer(instance=comments, many=True)
                    response.data = {"message": token_msg, "data": serializer.data}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response






class CommentUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Comment.objects.filter(id__gte=0)
    serializer_class = CommentEditSerializer
    
    
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
                    groups = ["superuser", "admin", "student", "teacher"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                if user_group.first().name == "teacher" or user_group.first().name == "student":
                    comments = Comment.objects.filter(id=self.kwargs.get("pk"), user_id=user.first().id)
                if user_group.first().name == "superuser" or user_group.first().name == "admin":
                    comments = Comment.objects.filter(id=self.kwargs.get("pk"))
                if comments.exists():
                    serializer = CommentEditSerializer(instance=comments, many=True)
                    response.data = {"message": token_msg, "data": serializer.data}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": "No comment found", "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                # ////////////////////////////////////////////////////////////
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
                    groups = ["superuser", "admin"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                instance = self.get_object()
                instance.updated_at = timezone.now()
                instance.content = request.data["content"]
                instance.save()
                serializer = self.get_serializer(instance)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    
    
    
    
    


class CommentStatusAPIView(RetrieveUpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentChangeStatusSerializer

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
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                instance = self.get_object()
                if request.data.get("status") == 'true':
                    instance.closed_at = timezone.now()
                    instance.status = True
                if request.data.get("status") == 'false':
                    instance.closed_at = timezone.now()
                    instance.status = False
                instance.save()
                serializer = self.get_serializer(instance)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response