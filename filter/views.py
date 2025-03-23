from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from account.token_permissions import OptionalTokenAuthentication


class ProductFilterListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [OptionalTokenAuthentication]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)

    #     # Capture applied filters
    #     applied_filters = {
    #         key: value.split(",") if "," in value else value
    #         for key, value in request.GET.items()
    #     }

    #     return Response({
    #         "filters_applied": applied_filters,
    #         "results": serializer.data,
    #     })
    def list(self, request, *args, **kwargs):
        print("Request received with query params:", request.GET)  # Debug request params

        queryset = self.filter_queryset(self.get_queryset())
        print("Filtered queryset count:", queryset.count())  # Debug queryset count

        serializer = self.get_serializer(queryset, many=True)
        
        applied_filters = {
            key: value.split(",") if "," in value else value
            for key, value in request.GET.items()
        }
        print("Applied filters:", applied_filters)  # Debug applied filters

        return Response({
            "filters_applied": applied_filters,
            "results": serializer.data,
        })    