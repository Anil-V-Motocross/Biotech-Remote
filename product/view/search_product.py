from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rapidfuzz import process, fuzz
from product.models import MainProduct, ProductCategory, ProductSubCategory, MainProductImage, Rating
from category.models import Category, SubCategory
from product.serializers import MainProductSerializer
from account.token_permissions import OptionalTokenAuthentication
from rest_framework.permissions import AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([OptionalTokenAuthentication])
def search_products(request):
    try:
        query = request.data.get('search', '').strip().lower()
        if not query:
            return Response(data={"message": "No search query provided."}, status=400)

        # Fetching all products
        product_queryset = MainProduct.objects.all()
        product_names = {p.name.lower(): p.id for p in product_queryset}  # Convert names to lowercase

        # Fuzzy match product names
        product_matches = process.extract(query, product_names.keys(), scorer=fuzz.partial_ratio, limit=10)
        threshold = 40  # Adjust for strictness
        matched_product_ids = [product_names[name] for name, score, _ in product_matches if score >= threshold]

        # Fetching products by ID
        matched_products = MainProduct.objects.filter(id__in=matched_product_ids)

        # Fetching categories & subcategories
        category_queryset = Category.objects.all()
        subcategory_queryset = SubCategory.objects.all()
        category_names = {c.name.lower(): c.id for c in category_queryset}
        subcategory_names = {s.name.lower(): s.id for s in subcategory_queryset}

        # Fuzzy match category & subcategory names
        category_matches = process.extract(query, category_names.keys(), scorer=fuzz.partial_ratio, limit=10)
        subcategory_matches = process.extract(query, subcategory_names.keys(), scorer=fuzz.partial_ratio, limit=10)

        matched_category_ids = [category_names[name] for name, score, _ in category_matches if score >= threshold]
        matched_subcategory_ids = [subcategory_names[name] for name, score, _ in subcategory_matches if score >= threshold]

        # Fetch related products from matched categories & subcategories
        category_product_ids = ProductCategory.objects.filter(category_id__in=matched_category_ids).values_list("product_id", flat=True)
        subcategory_product_ids = ProductSubCategory.objects.filter(subcategory_id__in=matched_subcategory_ids).values_list("product_id", flat=True)

        # Combine results (product name matches first, then category & subcategory)
        all_product_ids = list(matched_product_ids) + list(category_product_ids) + list(subcategory_product_ids)
        final_products = MainProduct.objects.filter(id__in=all_product_ids).distinct()

        # Sort: Ensure product name matches appear first
        sorted_products = sorted(
            final_products, 
            key=lambda p: matched_product_ids.index(p.id) if p.id in matched_product_ids else len(matched_product_ids)
        )

        # Serialize & return response
        serializer = MainProductSerializer(sorted_products, many=True, context={'request': request})
        return Response(data={"message": "success", "products": serializer.data}, status=200)

    except Exception as e:
        return Response(data={"message": "An error occurred", "error": str(e)}, status=500)
