from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from rest_framework.response import Response

class ProductFilterListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Capture applied filters
        applied_filters = {
            key: value.split(",") if "," in value else value
            for key, value in request.GET.items()
        }

        return Response({
            "filters_applied": applied_filters,
            "results": serializer.data,
        })