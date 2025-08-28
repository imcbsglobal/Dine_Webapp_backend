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
    



# views.py (add this to your existing views.py file)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DineBill
from .serializers import DineBillSerializer
from django.db.models import Q

@api_view(['GET'])
def dine_bill_api(request):
    """
    GET /api/bills/                    -> get all bills
    GET /api/bills/?billno=123         -> get specific bill by bill number
    GET /api/bills/?user=username      -> get bills by user
    GET /api/bills/?start_date=2024-01-01&end_date=2024-12-31  -> get bills by date range
    """
    
    try:
        # Start with all bills
        bills = DineBill.objects.all()
        
        # Filter by bill number if provided
        billno = request.query_params.get('billno')
        if billno:
            bills = bills.filter(billno=billno)
        
        # Filter by user if provided
        user = request.query_params.get('user')
        if user:
            bills = bills.filter(user_field__icontains=user)
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            bills = bills.filter(time_field__date__gte=start_date)
        
        if end_date:
            bills = bills.filter(time_field__date__lte=end_date)
        
        # Order by bill number (latest first)
        bills = bills.order_by('-billno')
        
        # Serialize the data
        serializer = DineBillSerializer(bills, many=True)
        
        # Calculate total amount for filtered results
        total_amount = sum(float(bill.amount or 0) for bill in bills)
        
        return Response({
            'status': 'success',
            'count': len(serializer.data),
            'total_amount': total_amount,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)