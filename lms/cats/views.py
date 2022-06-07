from functools import reduce
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_302_FOUND, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_406_NOT_ACCEPTABLE
from courses.models import Course
from courses.models import User_Course
from users.utils import decode_token

from cats.models import Cat
from cats.serializers import CatSerializer


class CatsCreateView(CreateAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    
    
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
                    groups = ["teacher", "superuser", "admin"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                find_cat = Cat.objects.filter(cat=request.data["cat"])
                if find_cat.exists():
                    response.data = {"message": token_msg, "data": find_cat.all().values()}
                    response.status_code = HTTP_302_FOUND
                else:
                    cats = self.create(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": cats.data}
                    response.status_code = HTTP_200_OK
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


class CatsListView(ListAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer


class CatsEditView(RetrieveUpdateAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
