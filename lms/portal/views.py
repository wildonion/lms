


from functools import reduce
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_402_PAYMENT_REQUIRED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE, HTTP_417_EXPECTATION_FAILED
from users.utils import decode_token
from .models import *
from django.conf import settings
from products.models import Product
from courses.models import Course
import json, requests
from django.shortcuts import redirect
from django.utils import timezone
from courses.models import User_Course
from .serializers import *









# -------------------------
# --- Create Payment API
# -------------------------
@api_view(['POST'])
def create_payment(request):
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
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none teacher or superuser group"}, status=HTTP_403_FORBIDDEN)
            else:
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            ZP_merchant_code = settings.ZARINPAL_MERCHANT_CODE
            zp_callback_url = settings.ZARINPAL_CALLBACK_URL
            zp_start_pay = settings.ZARINPAL_API_STARTPAY
            zp_request = settings.ZARINPAL_API_REQUEST
            find_product = Product.objects.filter(id=request.data["product_id"])
            if find_product.exists():
                amount = request.data["price"]
                find_course = Course.objects.filter(id=find_product.first().course_id)
                description = f"خرید دوره {find_course.first().title}" if find_course.exists() else "" 
                req_data = {
                    "merchant_id": ZP_merchant_code,
                    "amount": amount,
                    "callback_url": zp_callback_url,
                    "description": description,
                    "metadata": [{"mobile": "", "email": ""}]
                }
                req_header = {"accept": "application/json","content-type": "application/json'"}
                res = requests.post(url=zp_request, data=json.dumps(req_data), headers=req_header).json()
                if len(res['errors']) == 0:
                    authority = res["data"]["authority"]
                    product_id = request.data["product_id"]
                    user_id = user.first().id
                    zp_start_pay += f"{authority}"
                    created_payment = PaymentInfo(authority=authority, product_id=product_id, user_id=user_id, fee=amount) 
                    created_payment.save()
                    response.data = {'message': "Do redirect", "data": zp_start_pay}
                    response.status_code = HTTP_200_OK
                else:
                    e_code = res["errors"]["code"]
                    e_message = res["errors"]["message"]
                    response.data = {'message': token_msg, "data": f"{e_message} with code {e_code}"}
                    response.status_code = HTTP_417_EXPECTATION_FAILED
            else:
                response.data = {"message": token_msg, "data": []} # NOTE - product not found
                response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response






# -------------------------
# --- Callback API
# -------------------------
@api_view(['GET'])
def callback(request):
    response = Response()
    zp_verify = settings.ZARINPAL_API_VERIFY
    ZP_merchant_code = settings.ZARINPAL_MERCHANT_CODE
    t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        find_payment = PaymentInfo.objects.filter(authority=t_authority)
        if find_payment.exists():
            req_header = {"accept": "application/json", "content-type": "application/json'"}
            req_data = {
                "merchant_id": ZP_merchant_code,
                "amount": find_payment.first().fee,
                "authority": t_authority
            }
            res = requests.post(url=zp_verify, data=json.dumps(req_data), headers=req_header).json()
            if len(res['errors']) == 0:
                t_status = res['data']['code']
                if t_status == 100:
                    user_course = User_Course.objects.create(
                        payment_info_id=find_payment.first().id,
                        course_id=Product.objects.filter(id=find_payment.first().product_id).first().course_id, 
                        user_id=find_payment.first().user_id
                        )                    
                    PaymentInfo.objects.filter(id=find_payment.first().id).update(
                            ref_id=str(res['data']['ref_id']), 
                            verification_code=str(res['data']['code']),
                            card_pan=str(res['data']['card_pan']),
                            card_hash=str(res['data']['card_hash']),
                            fee_type=str(res['data']['fee_type']),
                            paid_at=timezone.now()
                    )
                    response.data = {"message": f'Transaction success with RefID: ' + str(res['data']['ref_id'])}
                    response.status_code = HTTP_201_CREATED
                elif t_status == 101:
                    response.data = {"message": 'Transaction already submitted: ' + str(res['data']['message'])}
                    response.status_code = HTTP_302_FOUND
                else:
                    response.data = {"message": 'Transaction failed with Status: ' + str(res['data']['code'])}
                    response.status_code = HTTP_417_EXPECTATION_FAILED
            else:
                e_code = res['errors']['code']
                e_message = res['errors']['message']
                response.data = {"message": f"Error code: {e_code}, Error Message: {e_message}"}
                response.status_code = None
        else:
            response.data = {"message": "No payment info found", "data": []} # NOTE - payment info not found
            response.status_code = HTTP_404_NOT_FOUND
    else:
        response.data = {"message": 'Transaction failed or canceled by user'}
        response.status_code = HTTP_402_PAYMENT_REQUIRED
    return response








# -------------------------------------
# --- Get All Successful Payments API
# -------------------------------------
@api_view(['POST'])
def get_suc_payments(request):
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
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            all_user_payments_for_superuser = False if "user_id" in request.data else True
            if all_user_payments_for_superuser:
                payments = PaymentInfo.objects.all()
                serializer = PaymentInfoSerializer(instance=payments, many=True)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
            else:
                find_user_payments = PaymentInfo.objects.filter(user_id=request.data["user_id"])
                if find_user_payments.exists():
                    all_user_payemnts = []
                    for p in find_user_payments.all():
                        user_payments = {}
                        if p.ref_id != "":
                            find_product = Product.objects.filter(id=p.product_id)
                            serializer = ProductSerializer(instance=find_product, many=True)
                            user_payments["product_info"] = serializer.data[0]
                            user_payments["id"] = p.id
                            user_payments["user_id"] = p.user_id
                            user_payments["verification_code"] = p.verification_code
                            user_payments["ref_id"] = p.ref_id
                            user_payments["requested_at"] = p.requested_at
                            user_payments["paid_at"] = p.paid_at
                            all_user_payemnts.append(user_payments)
                        else:
                            # NOTE - unsuccessful payment
                            pass
                    response.data = {"message": token_msg, "data": all_user_payemnts}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response









# -------------------------------------
# --- Get All Unsuccessful Payments API
# -------------------------------------
@api_view(['POST'])
def get_unsuc_payments(request):
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
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            all_user_payments_for_superuser = False if "user_id" in request.data else True
            if all_user_payments_for_superuser:
                payments = PaymentInfo.objects.all()
                serializer = PaymentInfoSerializer(instance=payments, many=True)
                response.data = {"message": token_msg, "data": serializer.data}
                response.status_code = HTTP_200_OK
            else:
                find_user_payments = PaymentInfo.objects.filter(user_id=request.data["user_id"])
                if find_user_payments.exists():
                    all_user_payemnts = []
                    for p in find_user_payments.all():
                        user_payments = {}
                        if p.ref_id == "":
                            find_product = Product.objects.filter(id=p.product_id)
                            serializer = ProductSerializer(instance=find_product, many=True)
                            user_payments["product_info"] = serializer.data[0]
                            user_payments["id"] = p.id
                            user_payments["user_id"] = p.user_id
                            user_payments["verification_code"] = p.verification_code
                            user_payments["ref_id"] = p.ref_id
                            user_payments["requested_at"] = p.requested_at
                            user_payments["paid_at"] = p.paid_at
                            all_user_payemnts.append(user_payments)
                        else:
                            # NOTE - successful payment
                            pass
                    response.data = {"message": token_msg, "data": all_user_payemnts}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response







# -------------------------------------
# --- Get All Unsuccessful Payments API
# -------------------------------------
@api_view(['POST'])
def get_payments(request):
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
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            payments = PaymentInfo.objects.all()
            serializer = PaymentInfoSerializer(instance=payments, many=True)
            response.data = {"message": token_msg, "data": serializer.data}
            response.status_code = HTTP_200_OK
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response






# -------------------------
# --- Get Single Payment API
# -------------------------
@api_view(['POST'])
def get_payment(request):
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
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            if user_group.first().name == "student":
                payment = PaymentInfo.objects.filter(id=request.data["payment_id"], user_id=user.first().id)
                if payment.exists():
                    payment_info = {}
                    find_product = Product.objects.filter(id=payment.first().product_id)
                    serializer = ProductSerializer(instance=find_product, many=True)
                    payment_info["product_info"] = serializer.data[0]
                    payment_info["id"] = payment.first().id
                    payment_info["user_id"] = payment.first().user_id
                    payment_info["verification_code"] = payment.first().verification_code
                    payment_info["ref_id"] = payment.first().ref_id
                    payment_info["requested_at"] = payment.first().requested_at
                    payment_info["paid_at"] = payment.first().paid_at
                    response.data = {"message": token_msg, "data": payment_info}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
            if user_group.first().name == "superuser":          
                payment = PaymentInfo.objects.filter(id=request.data["payment_id"])
                if payment.exists():
                    serializer = PaymentInfoSerializer(instance=payment, many=True)
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
