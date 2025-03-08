from product.serializers import MainProductSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from product.models import MainProduct
from django.shortcuts import get_object_or_404
from category.models import Category, SubCategory
from product.models import ProductCategory, MainProduct, ProductSubCategory


@api_view(['GET'])
def category_products(request, pk):
    try:
        # Check if the category exists
        category = get_object_or_404(Category, id=pk)

        # Find MainProduct IDs associated with this category
        main_product_ids = ProductCategory.objects.filter(category_id=category).values_list('product_id', flat=True)

        # Fetch MainProducts using the correct field
        products = MainProduct.objects.filter(id__in=main_product_ids)

        # Serialize & return response
        serializer = MainProductSerializer(products, many=True, context={'request': request})
        return Response(data={"message": "success", "products": serializer.data}, status=200)

    except Exception as e:
        return Response(data={"message": "An error occurred", "error": str(e)}, status=500)


@api_view(['GET'])
def category_products(request, pk):
    try:
        # Check if the category exists
        category = get_object_or_404(Category, id=pk)

        # Find MainProduct IDs associated with this category
        main_product_ids = ProductCategory.objects.filter(category_id=category).values_list('product_id', flat=True)

        # Fetch MainProducts using the correct field
        products = MainProduct.objects.filter(id__in=main_product_ids)

        # Serialize & return response
        serializer = MainProductSerializer(products, many=True, context={'request': request})
        return Response(data={"message": "success", "products": serializer.data}, status=200)

    except Exception as e:
        return Response(data={"message": "An error occurred", "error": str(e)}, status=500)


@api_view(['GET'])
def subcategory_products(request, pk):
    try:
        # Check if the subcategory exists
        subcategory = get_object_or_404(SubCategory, id=pk)
        print("Subcategory:", subcategory)

        # Find MainProduct IDs associated with this subcategory
        main_product_ids = ProductSubCategory.objects.filter(subcategory_id=subcategory).values_list('product_id', flat=True)
        print("Main Product IDs in SubCategory:", list(main_product_ids))

        # Fetch MainProducts using the correct field
        products = MainProduct.objects.filter(id__in=main_product_ids)
        print("Filtered MainProducts:", products)

        # Serialize & return response
        serializer = MainProductSerializer(products, many=True, context={'request': request})
        return Response(data={"message": "success", "products": serializer.data}, status=200)

    except Exception as e:
        return Response(data={"message": "An error occurred", "error": str(e)}, status=500)
