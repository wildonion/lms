from functools import reduce
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.utils import timezone
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from users.utils import decode_token
from .models import Proposal
from .serializers import ProposalSerializer, ProposalStatusSerializer, ProposalEditSerializer, ProposalViewSerializer, ImageSerializer, VideoSerializer
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





class ProposalListAPIView(ListAPIView):
    queryset = Proposal.published_objects.all()
    serializer_class = ProposalViewSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'short_description', 'content', ]

    def get(self, request, *args, **kwargs):
        response = Response()
        published_proposal = self.list(request, *args, **kwargs)
        if published_proposal.data:
            for pp in published_proposal.data:
                if pp["image"] != None:
                    pp["image"] = pp["image"][21:]
            response.data = {"message": "Fetched successfully", "data": published_proposal.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No published proposal found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response






class AllProposalListAPIView(ListAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalViewSerializer


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
                all_proposals = self.list(request, *args, **kwargs)
                for proposal in all_proposals.data:
                    if proposal["image"] != None:
                        proposal["image"] = proposal["image"][21:]
                response.data = {"message": token_msg, "data": all_proposals.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response









class ProposalEditAPIView(RetrieveUpdateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalEditSerializer
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
                updated_proposal = self.partial_update(request, *args, **kwargs)
                updated_proposal.data["image"] = updated_proposal.data["image"][21:] if updated_proposal.data["image"] != None else ''
                response.data = {"message": token_msg, "data": updated_proposal.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


class ProposalCreateAPIView(CreateAPIView):
    queryset = Proposal.published_objects.all()
    serializer_class = ProposalSerializer

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
                created_proposal = self.create(request, *args, **kwargs)
                created_proposal.data["image"] = created_proposal.data["image"][21:] if created_proposal.data["image"] != None else ''
                response.data = {"message": token_msg, "data": created_proposal.data}
                response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    
    
    
    

class ProposalChangeStatus(RetrieveUpdateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalStatusSerializer
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
