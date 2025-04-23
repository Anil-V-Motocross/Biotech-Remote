from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Max, Subquery, OuterRef
from order.models import OrderStatus
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import IsStaffUser

class ProcessingOrdersCountView(ListAPIView):
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        try:
            # Get the latest status ID for each order
            latest_status_ids = (
                OrderStatus.objects
                .filter(order=OuterRef('order'))
                .order_by('-timestamp')
                .values('id')[:1]
            )

            # Get latest statuses using Subquery
            latest_statuses = OrderStatus.objects.filter(
                id__in=Subquery(latest_status_ids)
            )

            # Filter those with status = 'PROCESSING'
            processing_count = latest_statuses.filter(status='PROCESSING').count()
            processing_request = latest_statuses.filter(status='RETURN_REQUESTED').count()
            total =  processing_count + processing_request

            return Response(
                data={
                        'total_notifications':total,
                        'orders_count': processing_count,
                        'return_request_count': processing_request
                      },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={'message': 'Something went wrong', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
