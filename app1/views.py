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
    





from django.db.models import Sum, Count
from django.db.models.functions import TruncDate

@api_view(['GET'])
def bill_day_summary(request):
    """
    GET /api/bill-day-summary/
    -> Returns total bill amount and count grouped by each day
    """
    try:
        # Group bills by date
        summary = (
            DineBill.objects
            .values(date=TruncDate('time_field'))
            .annotate(
                total_bill_amount=Sum('amount'),
                total_bill_count=Count('billno')
            )
            .order_by('-date')
        )

        return Response({
            'status': 'success',
            'count': summary.count(),
            'data': list(summary)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DineBillMonth
from .serializers import DineBillMonthSerializer
from django.db.models import Sum, Count
from django.db.models.functions import Extract
import calendar
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DineBillMonthAPIView(APIView):
    def get(self, request):
        """
        GET endpoint for monthly bill summary
        Returns all 12 months of current year with their data
        Shows 0 for months with no data
        """
        try:
            current_year = datetime.now().year
            
            # Get monthly data from DineBillMonth for current year
            monthly_data = (
                DineBillMonth.objects
                .filter(date_field__year=current_year)
                .values(month=Extract('date_field', 'month'))
                .annotate(
                    total_amount=Sum('amount'),
                    total_count=Count('billno')
                )
                .order_by('month')
            )
            
            # Convert to dictionary for easy lookup
            data_dict = {item['month']: item for item in monthly_data}
            
            # Create result for all 12 months
            result_data = []
            for month in range(1, 13):
                month_data = data_dict.get(month, {})
                result_data.append({
                    'month': month,
                    'month_name': calendar.month_name[month],
                    'total_amount': month_data.get('total_amount', 0) or 0,
                    'total_count': month_data.get('total_count', 0)
                })
            
            # Serialize the data
            serializer = DineBillMonthSerializer(result_data, many=True)
            
            # Calculate yearly totals
            yearly_total_amount = sum(item['total_amount'] for item in result_data)
            yearly_total_count = sum(item['total_count'] for item in result_data)
            
            return Response({
                'status': 'success',
                'year': current_year,
                'yearly_total_amount': yearly_total_amount,
                'yearly_total_count': yearly_total_count,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching monthly bill data: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DineBill, CancelledBills
from .serializers import DineCancelledBillsSerializer
import logging

logger = logging.getLogger(__name__)

# Add this view class to your views.py file
class DineCancelledBillsAPIView(APIView):
    def get(self, request):
        """
        GET endpoint for dinecancelledbills
        Returns: date, billno, creditcard, colnstatus
        Combines data from DineBill and CancelledBills tables
        """
        try:
            from django.db import connection
            
            # Raw SQL query to join both tables based on billno
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(cb.date, db.date) as date,
                        cb.billno,
                        cb.creditcard,
                        cb.colnstatus
                    FROM cancelled_bills cb
                    LEFT JOIN dine_bill db ON cb.billno = db.billno
                    ORDER BY cb.billno DESC
                """)
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result_data = []
                for row in rows:
                    result_data.append({
                        'date': row[0],
                        'billno': row[1],
                        'creditcard': row[2],
                        'colnstatus': row[3]
                    })
            
            # Serialize the data
            serializer = DineCancelledBillsSerializer(result_data, many=True)
            
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching dine cancelled bills: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Alternative implementation using Django ORM join (more Django-like approach)
class DineCancelledBillsAPIViewAlternative(APIView):
    def get(self, request):
        """
        Alternative implementation using Django ORM
        """
        try:
            from django.db import connection
            
            # Raw SQL query to join both tables
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(cb.date, db.date) as date,
                        cb.billno,
                        cb.creditcard,
                        cb.colnstatus
                    FROM cancelled_bills cb
                    LEFT JOIN dine_bill db ON cb.billno = db.billno
                    ORDER BY cb.billno DESC
                """)
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result_data = []
                for row in rows:
                    result_data.append({
                        'date': row[0],
                        'billno': row[1],
                        'creditcard': row[2],
                        'colnstatus': row[3]
                    })
            
            # Serialize the data
            serializer = DineCancelledBillsSerializer(result_data, many=True)
            
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching cancelled bills: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DineKotSalesDetailSerializer
import logging

logger = logging.getLogger(__name__)

class DineKotSalesDetailAPIView(APIView):
    def get(self, request):
        """
        GET endpoint for dine-kot-sales-detail
        Returns: date, item_name, total_qty, total_amount
        Joins DineBill, DineKotSalesDetail, and TbItemMaster tables
        Groups by date and item to show daily summary
        """
        try:
            from django.db import connection
            
            # Raw SQL query to join all three tables and group by date and item
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        db.date as date,
                        COALESCE(tim.item_name, dksd.item) as item_name,
                        SUM(dksd.qty) as total_qty,
                        SUM(dksd.qty * dksd.rate) as total_amount
                    FROM dine_bill db
                    INNER JOIN dine_kot_sales_detail dksd ON db.billno = dksd.billno
                    LEFT JOIN tb_item_master tim ON dksd.item = tim.item_code
                    WHERE db.date IS NOT NULL
                    GROUP BY db.date, tim.item_name, dksd.item
                    ORDER BY db.date DESC, tim.item_name ASC
                """)
                
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                result_data = []
                for row in rows:
                    result_data.append({
                        'date': row[0],
                        'item_name': row[1],
                        'total_qty': row[2],
                        'total_amount': row[3]
                    })
            
            # Serialize the data
            serializer = DineKotSalesDetailSerializer(result_data, many=True)
            
            return Response({
                'status': 'success',
                'count': len(serializer.data),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching dine kot sales detail: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)