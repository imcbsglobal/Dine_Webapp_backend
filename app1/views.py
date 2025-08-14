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





# views.py  (append)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TbItemMaster
from .serializers import TbItemMasterSerializer

# GET  /api/items/        -> list all items
# POST /api/items/        -> create / update many items (sync)
@api_view(['GET', 'POST'])
def item_master_api(request):
    if request.method == 'GET':
        items = TbItemMaster.objects.all()
        serializer = TbItemMasterSerializer(items, many=True)
        return Response({
            'status': 'success',
            'count': len(serializer.data),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = request.data
        if isinstance(data, dict):
            data = [data]

        created = updated = 0
        errors = []

        for rec in data:
            item_code = rec.get('item_code')
            if not item_code:
                errors.append({'record': rec, 'error': 'item_code is required'})
                continue

            try:
                item = TbItemMaster.objects.get(item_code=item_code)
                ser = TbItemMasterSerializer(item, data=rec, partial=True)
                if ser.is_valid():
                    ser.save()
                    updated += 1
                else:
                    errors.append({'record': rec, 'error': ser.errors})
            except TbItemMaster.DoesNotExist:
                ser = TbItemMasterSerializer(data=rec)
                if ser.is_valid():
                    ser.save()
                    created += 1
                else:
                    errors.append({'record': rec, 'error': ser.errors})

        resp = {'status': 'success', 'created': created, 'updated': updated, 'errors': errors}
        if errors:
            resp['status'] = 'partial_success'
        return Response(resp, status=status.HTTP_200_OK)