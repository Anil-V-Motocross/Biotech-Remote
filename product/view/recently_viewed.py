import random
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from product.models import MainProduct, RecentlyViewedProduct, ProductViewCount
from product.serializers import MainProductSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class RecentlyViewedProductsView(generics.ListAPIView):
    serializer_class = MainProductSerializer
    permission_classes = [AllowAny]  # Allow all users, even without authentication

    def get_queryset(self):
        print("🔹 API called: RecentlyViewedProductsView")  # Debugging

        viewed_products = []
        user = self.request.user if self.request.user.is_authenticated else None
        print(f"✅ User: {user}")

        if user:
            recently_viewed = RecentlyViewedProduct.objects.filter(user=user).order_by('-viewed_at')[:4]
            viewed_products = [entry.product for entry in recently_viewed]
            print(f"✅ Recently viewed products count: {len(viewed_products)}")

        if not viewed_products:
            most_viewed = ProductViewCount.objects.all().order_by('-count')[:4]
            viewed_products = [entry.product for entry in most_viewed]
            print(f"✅ Mostly viewed products count: {len(viewed_products)}")

        return viewed_products

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset:
            print("❌ No products available")
            return Response({'message': 'No products available', 'data': []}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        print("✅ Successfully returning products")
        return Response({'message': 'success', 'data': {'products': serializer.data}}, status=status.HTTP_200_OK)