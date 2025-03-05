from rest_framework.response import Response
from product.models import Product
from account.permissions import DynamicPermission
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status


@api_view(['GET'])
# @permission_classes([IsAuthenticated, DynamicPermission])
# @authentication_classes([JWTAuthentication])
def check_product_quantity(request, product_id):
    if request.method == 'GET':
        # required_permissions = ['product.view_product']
        # if not any(request.user.has_perm(perm) for perm in required_permissions):
        #     return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)     

        try:
            selected_product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(data={'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        stock = selected_product.stock
        quantity = request.query_params.get('quantity')
        action = request.query_params.get('action')  # 'increment' or 'decrement'

        if quantity is None:
            return Response(data={'status': False, 'message': 'Quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity) 
        except ValueError:
            return Response(data={'status': False, 'message': 'Invalid quantity value'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response(data={'status': False, 'message': 'Quantity must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'increment':
            new_quantity = quantity + 1
            if new_quantity > stock:
                return Response(data={'status': False, 'message': "Stock exceeded", 'new_quantity': stock}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={'status': True, 'new_quantity': new_quantity, 'message': "Quantity increased"}, status=status.HTTP_200_OK)

        elif action == 'decrement':
            new_quantity = quantity - 1
            if new_quantity < 1:
                return Response(data={'status': False, 'message': "Quantity should be 1 or greater", 'new_quantity': quantity}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={'status': True, 'new_quantity': new_quantity, 'message': "Quantity decreased"}, status=status.HTTP_200_OK)

        return Response(data={'status': False, 'message': "No valid action provided. Use 'increment' or 'decrement'."}, status=status.HTTP_400_BAD_REQUEST)


