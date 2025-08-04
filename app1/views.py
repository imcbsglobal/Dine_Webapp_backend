from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AccUsers
from .serializers import AccUsersSerializer

@api_view(['POST'])
def login_user(request):
    user_id = request.data.get('id')
    password = request.data.get('password')

    try:
        user = AccUsers.objects.get(id=user_id)
        if user.pass_field == password:
            return Response({'status': 'success', 'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'fail', 'message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    except AccUsers.DoesNotExist:
        return Response({'status': 'fail', 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_users(request):
    users = AccUsers.objects.all()
    serializer = AccUsersSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
