from .models import CustomUser, UserTransaction
from rest_framework.decorators import api_view
from .serializers import UserSerializer, UserTransactionSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.views import APIView
from .utils import generate_access_token, decode_token, SECRET_KEY, token_required


@api_view(['POST'])
def register_user(request):

    """
      Registers a new user. Expects username, email, and password in the request data.
      If valid, creates and returns the user data.
      """
    # Initialize serializer with request data
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):

    """
      Logs in a user using either username or email and password.
      If successful, generates and returns an access token.
      """

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
    if not (user.check_password(password)):
        return Response({'error': 'Incorrect Password'}, status=status.HTTP_400_BAD_REQUEST)
    if user:
        # Generate an access token for the user
        access_token = generate_access_token(user)
        user.is_login = True  # Set user as logged in
        user.is_active = True # Ensure user is active
        user.token = str(access_token)
        user.save()
        user_data = UserSerializer(user).data
        return Response({'data': {'token': access_token, **user_data, }}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@token_required  # Decorator to ensure the user is authenticated
def user_logout(request):

    """
       Logs out the user by invalidating the access token.
       """

    try:
        user_id = request.user_id
        user_inst = CustomUser.objects.get(id=user_id)  # Find the user instance
        user_inst.token = None
        user_inst.save()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def deposit(request):

    """
       Allows the user to deposit an amount into their account.
       Validates the deposit amount and updates the balance.
       """

    try:
        user_id = request.user_id
        deposit_amount = request.data.get('deposit_amount')

        try:
            if float(deposit_amount) <= 0:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.open_balance
        new_open_balance = current_amount + deposit_amount
        user_inst.open_balance = new_open_balance

        # Create a transaction record for the deposit
        transaction = UserTransaction.objects.create(user_id=user_inst, deposit_amount=deposit_amount,
                                                      withdraw=0, transaction_type="Deposit")
        transaction.save()
        user_inst.save()

        return Response({"message": "Amount deposited successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def withdraw(request):

    """
        Allows the user to withdraw an amount from their account.
        Validates the withdrawal amount and updates the balance.
        """

    try:
        user_id = request.user_id
        withdraw = request.data.get('withdraw')

        try:
            if float(withdraw) <= 0:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        user_inst = CustomUser.objects.get(id=user_id)
        current_amount = user_inst.open_balance
        new_open_balance = current_amount - withdraw
        user_inst.open_balance = new_open_balance

        # Create a transaction record for the withdrawal
        transaction = UserTransaction.objects.create(user_id=user_inst, deposit_amount=0,
                                                     withdraw=withdraw, transaction_type="Withdraw")
        transaction.save()
        user_inst.save()

        return Response({"message": "Withdraw Amount successfully"}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@token_required
def check_balance(request):

    """
     Returns the current balance of the user.
     """

    try:
        user_id = request.user_id
        user_inst = CustomUser.objects.get(id=user_id)
        balance = user_inst.open_balance  # Get current balance

        return Response({"balance": balance}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@token_required
def transaction_history(request):

    """
      Returns the transaction history for the user along with the final balance.
      """

    try:
        user_id = request.user_id
        user = CustomUser.objects.get(id=user_id)
        # Get all transactions for the user
        transactions = UserTransaction.objects.filter(user_id=user_id)
        transaction_data = UserTransactionSerializer(transactions, many=True).data

        initial_amount = user.initial_amount
        # Calculate total deposits
        total_deposits = sum(transaction.deposit_amount for transaction in transactions)
        # Calculate total withdrawals
        total_withdrawals = sum(transaction.withdraw for transaction in transactions)

        # Calculate the final balance
        final_balance = total_deposits - total_withdrawals

        return Response({"transaction": transaction_data, "final_balance": final_balance,
                         "initial_amount": initial_amount}, status=status.HTTP_200_OK)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


