from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework import status
from rest_framework.response import Response
from product.models import Rating, Review, Product
from order.models import Order
from product.serializers import RatingReviewSerializer
from django.db.models import Q
from account.models import User

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
    products = Product.objects.filter(product_id=main_product_id)

    orders = Order.objects.filter(
        customer_id=user,
        orderitem__product_id__in=products
    )

    delivered_orders = orders.filter(status="delivered")

    has_purchased = delivered_orders.exists()

    if not has_purchased:
        return Response({'message': 'You can only review a product after delivery.'}, status=status.HTTP_403_FORBIDDEN)

    rating = Rating.objects.filter(main_product_id_id=main_product_id, user_id=user).first()
    review = Review.objects.filter(main_product_id_id=main_product_id, user_id=user).first()

    # user = User.objects.get(id=user.id)  # Replace with actual user ID
    # print("user permission and user   --- \n",user, " permission   --\n",user.get_all_permissions())

    if request.method == 'GET':
        required_permissions = ['product.view_rating', 'product.view_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        # Prepare response data
        response_data = {}
        if rating:
            response_data['product_rating'] = rating.product_rating
        if review:
            response_data['review_title'] = review.review_title
            response_data['product_review'] = review.product_review
            response_data['recommend'] = review.recommend

        if not response_data:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(data={'message': 'success', 'data': response_data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        required_permissions = ['product.add_rating', 'product.add_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RatingReviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'Rating and review added successfully.'}, status=status.HTTP_201_CREATED)
        
        return Response(data={'message': 'Validation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        required_permissions = ['product.change_rating', 'product.change_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure at least one exists
        if not rating and not review:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        # Extract and validate input data without triggering unnecessary purchase checks
        serializer = RatingReviewSerializer(instance=review or rating, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Update Rating if provided
            if 'product_rating' in validated_data and rating:
                rating.product_rating = validated_data['product_rating']
                rating.save()

            # Update Review if provided
            if review:
                review.review_title = validated_data.get('review_title', review.review_title)
                review.product_review = validated_data.get('product_review', review.product_review)
                review.recommend = validated_data.get('recommend', review.recommend)
                review.save()

            return Response(data={'message': 'Rating and review updated successfully.'}, status=status.HTTP_200_OK)

        return Response(data={'message': 'Validation failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        required_permissions = ['product.delete_rating', 'product.delete_review']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if not rating and not review:
            return Response(data={'message': 'No rating or review found for this product.'}, status=status.HTTP_404_NOT_FOUND)

        if rating:
            rating.delete()
        if review:
            review.delete()

        return Response(data={'message': 'Rating and review deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)