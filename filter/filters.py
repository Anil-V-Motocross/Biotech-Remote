import django_filters
from django_filters import rest_framework as filters
from product.models import Product
from django.db.models import Q

# class ProductFilter(filters.FilterSet):
#     type = django_filters.CharFilter(method='filter_by_type')
#     category = django_filters.CharFilter(field_name='product_id__productsubcategory__subcategory_id__name', lookup_expr='icontains')
#     price_min = django_filters.NumberFilter(field_name="sale_price", lookup_expr="gte")
#     price_max = django_filters.NumberFilter(field_name="sale_price", lookup_expr="lte")

#     size = django_filters.CharFilter(field_name="size_id__name", lookup_expr="icontains")
#     planter_size = django_filters.CharFilter(field_name="planter_size_id__name", lookup_expr="icontains")
#     planter = django_filters.CharFilter(field_name="planter_id__name", lookup_expr="icontains")
#     weights = django_filters.CharFilter(field_name="weight_id__size_grams", lookup_expr="exact")  
#     litre_size = django_filters.CharFilter(field_name="litre_id__name", lookup_expr="icontains")
#     color = django_filters.CharFilter(field_name="color_id__color_name", lookup_expr="icontains")

#     def filter_by_type(self, queryset, name, value):
#         return queryset.filter(product_id__type=value)

#     class Meta:
#         model = Product
#         fields = [
#             'type', 'category', 'price_min', 'price_max',
#             'size', 'planter_size', 'planter', 'weights', 'litre_size', 'color'
#             ]




class ProductFilter(django_filters.FilterSet):
    product_type = django_filters.CharFilter(field_name="product_id__type", lookup_expr="iexact")
    subcategories = django_filters.CharFilter(field_name="product_id__productsubcategory__subcategory_id__name", lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name="mrp", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="mrp", lookup_expr="lte")

    size = django_filters.CharFilter(method="filter_by_combinations")
    planter_size = django_filters.CharFilter(method="filter_by_combinations")
    planter = django_filters.CharFilter(method="filter_by_combinations")
    weights = django_filters.CharFilter(method="filter_by_combinations")
    litre_size = django_filters.CharFilter(method="filter_by_combinations")
    color = django_filters.CharFilter(method="filter_by_combinations")

    def filter_by_combinations(self, queryset, name, value):
        """
        Custom method to filter by multiple parameters while ensuring valid combinations.
        """
        values = value.split(",")  # Handle multiple values from query params 
        
        field_mapping = {
            "size": "size_id__name",
            "planter_size": "planter_size_id__name",
            "planter": "planter_id__name",
            "weights": "weight_id__size_grams",
            "litre_size": "litre_id__name",
            "color": "color_id__color_name",
        }

        if name not in field_mapping:
            return queryset  # Return original queryset if field is not mapped

        query = Q()
        for val in values:
            query |= Q(**{field_mapping[name]: val})

        return queryset.filter(query)

    class Meta:
        model = Product
        fields = ["product_type", "subcategories", "price_min", "price_max", "size", "planter_size", "planter", "weights", "litre_size", "color"]
