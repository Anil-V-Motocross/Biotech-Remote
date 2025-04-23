from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from product.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from account.token_permissions import OptionalTokenAuthentication
from rest_framework.pagination import PageNumberPagination

class ProductFilterListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = [OptionalTokenAuthentication]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = PageNumberPagination
        
    def list(self, request, *args, **kwargs):
        print("Request received with query params:", request.GET)

        queryset = self.filter_queryset(self.get_queryset())
        print("Filtered queryset count:", queryset.count())

        applied_filters = {
            key: value.split(",") if "," in value else value
            for key, value in request.GET.items()
        }
        print("Applied filters:", applied_filters)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response({
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "filters_applied": applied_filters,
                "results": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "filters_applied": applied_filters,
            "results": serializer.data
        })
        