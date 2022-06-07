from functools import reduce
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from users.utils import decode_token
from .models import Ticket
from .serializers import TicketListSerializer, create_Ticket_serializer, TicketEditSerializer, TicketChangeStatusSerializer






# NOTE - this is the main view to create a ticket and it will return an instance of the serializer
class TicketCreateAPIView(CreateAPIView):
    queryset = Ticket.objects.all()
    
    def get_serializer_class(self, *args, **kwargs):
        model_type = self.request.GET.get('type')
        slug = self.request.GET.get('slug')
        parent_id = self.request.GET.get('parent_id', None)
        user_id = self.request.GET.get('user_id', None)
        ticket = create_Ticket_serializer(model_type=model_type, slug=slug, parent_id=parent_id, user_id=user_id)
        return ticket
    
    
    
    
    
# NOTE - this is the proxy view to call the main view of creating ticket
class TicketCreateAPIViewPost(CreateAPIView):
    
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
                ticket = TicketCreateAPIView.as_view()(self.request._request) # NOTE - calling the main view with to create the ticket - self.request._request is the django http request and self.request is the django rest framework request object
                response.data = {"message": token_msg, "data": ticket.data}
                response.status_code = HTTP_201_CREATED
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response







class TicketListAPIView(ListAPIView):
    serializer_class = TicketListSerializer
    filter_backends = [SearchFilter]
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
                tickets = Ticket.objects.filter(id__gte=0)
                if tickets.exists():
                    serializer = TicketListSerializer(instance=tickets, many=True)
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


class TicketUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketEditSerializer
    
    
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
                    tickets = Ticket.objects.filter(id=self.kwargs.get("pk"), user_id=user.first().id)
                if user_group.first().name == "superuser" or user_group.first().name == "admin":
                    tickets = Ticket.objects.filter(id=self.kwargs.get("pk"))
                if tickets.exists():
                    serializer = TicketEditSerializer(instance=tickets, many=True)
                    response.data = {"message": token_msg, "data": serializer.data}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": "No ticket found", "data": []}
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




class TicketStatusAPIView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketChangeStatusSerializer

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
                if request.data.get("is_close") == 'true':
                    instance.closed_at = timezone.now()
                    instance.is_close = True
                if request.data.get("is_close") == 'false':
                    instance.closed_at = timezone.now()
                    instance.is_close = False
                instance.save()
                serializer = self.get_serializer(instance)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
