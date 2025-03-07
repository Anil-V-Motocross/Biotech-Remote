from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework import status
from rest_framework.response import Response
from product.models import Rating, Review
from order.models import Order
from product.serializers import RatingReviewSerializer

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def rating_review_create(request, main_product_id):
    """
    Handles Rating & Review:
    - GET: Retrieve a user's rating & review for a product.
    - POST: Create a new rating & review (only after product delivery).
    - PATCH: Update an existing rating & review.
    - DELETE: Remove an existing rating & review.
    """
    user = request.user

    # Ensure user has purchased and received the product
    has_purchased = Order.objects.filter(
        customer_id=user,
        orderitem__product__product_id=main_product_id,
        shipment__shipment_status="Delivered"
    ).exists()

    if not has_purchased:
        return Response(data={'message': 'You can only review a product after delivery.'}, status=status.HTTP_403_FORBIDDEN)

    # Fetch Rating & Review in one query
    rating = Rating.objects.filter(main_product_id=main_product_id, user_id=user).first()
    review = Review.objects.filter(main_product_id=main_product_id, user_id=user).first()

    if request.method == 'GET':
        required_permissions = ['rating.view_rating', 'review.view_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Return existing rating & review if available
        data = {}
        if rating:
            data['rating'] = rating.product_rating
        if review:
            data['review'] = review.product_review

        if not data:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        required_permissions = ['rating.add_rating', 'review.add_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RatingReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user_id=user, main_product_id=main_product_id)
            return Response(data={'message': 'Rating and review added successfully.'}, status=status.HTTP_201_CREATED)
        
        return Response(data={'message': 'Validation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        required_permissions = ['rating.change_rating', 'review.change_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if not rating and not review:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RatingReviewSerializer(rating or review, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Rating and review updated successfully.'}, status=status.HTTP_200_OK)
        
        return Response(data={'message': 'Validation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        required_permissions = ['rating.delete_rating', 'review.delete_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if not rating and not review:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        if rating:
            rating.delete()
        if review:
            review.delete()

        return Response(data={'message': 'Rating and review deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)