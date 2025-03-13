from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from product.models import Product, ProductSubCategory, Color, Size, PlanterSize, Planter, Weight, Litre, MainProduct

# class DynamicFilterView(APIView):
#     def get(self, request, *args, **kwargs):
#         product_type = request.query_params.get("type")  # Get product type from request
        
#         filters = {
#             "categories": list(ProductSubCategory.objects.values_list("subcategory_id__name", flat=True).distinct())
#         }

#         if product_type == "plant":
#             filters.update({
#                 "subcategories": list(ProductSubCategory.objects.filter(product_id__product_id__type="plant").values_list("subcategory_id__name", flat=True).distinct()),
#                 "price": {"min": Product.objects.filter(product_id__type="plant").order_by("sale_price").first().sale_price,
#                           "max": Product.objects.filter(product_id__type="plant").order_by("-sale_price").first().sale_price},
#                 "size": list(Size.objects.values_list("name", flat=True).distinct()),
#                 "planter_size": list(PlanterSize.objects.values_list("name", flat=True).distinct()),
#                 "planter": list(Planter.objects.values_list("name", flat=True).distinct()),
#                 "color": list(Color.objects.values_list("color_name", flat=True).distinct())
#             })

#         elif product_type == "seed":
#             filters.update({
#                 "subcategories": list(ProductSubCategory.objects.filter(product_id__product_id__type="seed").values_list("subcategory_id__name", flat=True).distinct()),
#                 "price": {"min": Product.objects.filter(product_id__type="seed").order_by("sale_price").first().sale_price,
#                           "max": Product.objects.filter(product_id__type="seed").order_by("-sale_price").first().sale_price},
#                 "weights": list(Weight.objects.values_list("size_grams", flat=True).distinct())
#             })

#         elif product_type == "pot":
#             filters.update({
#                 "subcategories": list(ProductSubCategory.objects.filter(product_id__product_id__type="pot").values_list("subcategory_id__name", flat=True).distinct()),
#                 "price": {"min": Product.objects.filter(product_id__type="pot").order_by("sale_price").first().sale_price,
#                           "max": Product.objects.filter(product_id__type="pot").order_by("-sale_price").first().sale_price},
#                 "planter_size": list(PlanterSize.objects.values_list("name", flat=True).distinct()),
#                 "litre_size": list(Litre.objects.values_list("name", flat=True).distinct()),
#                 "color": list(Color.objects.values_list("color_name", flat=True).distinct())
#             })

#         elif product_type == "tool":
#             filters.update({
#                 "subcategories": list(ProductSubCategory.objects.filter(product_id__product_id__type="tool").values_list("subcategory_id__name", flat=True).distinct()),
#                 "price": {"min": Product.objects.filter(product_id__type="tool").order_by("sale_price").first().sale_price,
#                           "max": Product.objects.filter(product_id__type="tool").order_by("-sale_price").first().sale_price},
#                 "size": list(Size.objects.values_list("name", flat=True).distinct()),
#                 "color": list(Color.objects.values_list("color_name", flat=True).distinct())
#             })

#         return Response(filters)



class DynamicFilterView(APIView):
    def get(self, request, *args, **kwargs):
        product_type = request.query_params.get("type")  # Get product type from request
        available_types = list(MainProduct.objects.values_list("type", flat=True).distinct())
        
        filters = {
            "available_types": available_types,
            # "subcategories": list(ProductSubCategory.objects.values_list("subcategory_id__name", flat=True).distinct())
        }

        if product_type == "plant":
            filters.update({
                "subcategories": list(ProductSubCategory.objects.filter(product_id__type="plant").values_list("subcategory_id__name", flat=True).distinct()),
                "price": {
                    "price_min": Product.objects.filter(product_id__type="plant").order_by("sale_price").first().sale_price,
                    "price_max": Product.objects.filter(product_id__type="plant").order_by("-sale_price").first().sale_price,
                } if Product.objects.filter(product_id__type="plant").exists() else {"min": 0, "max": 0},
                "size": list(Size.objects.values_list("name", flat=True).distinct()),
                "planter_size": list(PlanterSize.objects.values_list("name", flat=True).distinct()),
                "planter": list(Planter.objects.values_list("name", flat=True).distinct()),
                "color": list(Color.objects.values_list("color_name", flat=True).distinct())
            })

        elif product_type == "seed":
            filters.update({
                "subcategories": list(ProductSubCategory.objects.filter(product_id__type="seed").values_list("subcategory_id__name", flat=True).distinct()),
                "price": {
                    "price_min": Product.objects.filter(product_id__type="seed").order_by("sale_price").first().sale_price,
                    "price_max": Product.objects.filter(product_id__type="seed").order_by("-sale_price").first().sale_price,
                } if Product.objects.filter(product_id__type="seed").exists() else {"min": 0, "max": 0},
                "weights": list(Weight.objects.values_list("size_grams", flat=True).distinct())
            })

        elif product_type == "pot":
            filters.update({
                "subcategories": list(ProductSubCategory.objects.filter(product_id__type="pot").values_list("subcategory_id__name", flat=True).distinct()),
                "price": {
                    "price_min": Product.objects.filter(product_id__type="pot").order_by("sale_price").first().sale_price,
                    "price_max": Product.objects.filter(product_id__type="pot").order_by("-sale_price").first().sale_price,
                } if Product.objects.filter(product_id__type="pot").exists() else {"min": 0, "max": 0},
                "planter_size": list(PlanterSize.objects.values_list("name", flat=True).distinct()),
                "litre_size": list(Litre.objects.values_list("name", flat=True).distinct()),
                "color": list(Color.objects.values_list("color_name", flat=True).distinct())
            })

        elif product_type == "tool":
            filters.update({
                "subcategories": list(ProductSubCategory.objects.filter(product_id__type="tool").values_list("subcategory_id__name", flat=True).distinct()),
                "price": {
                    "min": Product.objects.filter(product_id__type="tool").order_by("sale_price").first().sale_price,
                    "max": Product.objects.filter(product_id__type="tool").order_by("-sale_price").first().sale_price,
                } if Product.objects.filter(product_id__type="tool").exists() else {"min": 0, "max": 0},
                "size": list(Size.objects.values_list("name", flat=True).distinct()),
                "color": list(Color.objects.values_list("color_name", flat=True).distinct())
            })

        return Response({"filters":filters})
