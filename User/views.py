import jwt
from django.db.migrations import serializer
from rest_framework.authtoken.models import Token


from .models import CustomUser, UserTransaction
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.views import APIView
from .utils import generate_access_token, generate_refresh_token, decode_token, SECRET_KEY, token_required


@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    username_or_email = request.data.get('username')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = None
    try:
        # Use Q objects to build the query
        user = CustomUser.objects.get(
            Q(username=username_or_email) | Q(email=username_or_email)
        )
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Check the password if the user is found
    if not(user.check_password(password)):
        return Response({'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        access_token = generate_access_token(user)
        # token, _ = Token.objects.get_or_create(user=user)
        user.token = str(access_token)
        user.save()
        # user_data = {
        #     'username': user.username,
        #     'amount': user.amount,
        #
        # }
        user_data = UserSerializer(user).data
        return Response({'token': access_token, 'data': user_data}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def user_logout(request):
    token_key = request.data.get('token')
    if not token_key:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        Token.objects.filter(key=token_key).delete()
        Token.objects.all()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return (Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST))


@api_view(['POST'])
@token_required
def deposit(request):
    try:
        user_id = request.user_id
        deposit_amount = request.data.get('deposit_amount')

        try:
            if float(deposit_amount) <= 0:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.initial_amount
        new_initial_amount = current_amount + deposit_amount
        user_inst.initial_amount = new_initial_amount

        transaction = UserTransaction.objects.create(user_id=user_inst, deposit_amount=deposit_amount, withdraw=0)
        transaction.save()
        user_inst.save()

        return Response({"message": "Amount deposited successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def withdraw(request):
    try:
        user_id = request.user_id
        withdraw = request.data.get('withdraw')

        try:
           if float(withdraw) <= 0:
               return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
           return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.initial_amount
        new_initial_amount = current_amount + withdraw
        user_inst.initial_amount = new_initial_amount

        transaction = UserTransaction.objects.create(user_id=user_inst,deposit_amount=0,withdraw=withdraw)
        transaction.save()
        user_inst.save()

        return Response({"message": "Withdraw Amount successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class RefreshTokenView(APIView):
    def post(self, request, utl=None):
        refresh_token = request.data.get('refresh')

        payload = utl.decode_token(refresh_token)
        if not payload:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = CustomUser.objects.get(id=payload['user_id'])
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        new_access_token = utl.generate_access_token(user)

        return Response({'access': new_access_token})