from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from combo.models import ComboOffer
from combo.serializers import ComboOfferSerializer

@api_view(['GET'])
def combo_offer_list(request):
    """
    Retrieve all active combo offers and shop the look offers separately.
    """
    try:
        # Get separate lists
        combo_offers = ComboOffer.objects.filter(is_active=True, is_shop_the_look=False).order_by('-date_created')
        shop_the_look_offers = ComboOffer.objects.filter(is_active=True, is_shop_the_look=True).order_by('-date_created')

        # Serialize results
        combo_serializer = ComboOfferSerializer(combo_offers, many=True)
        shop_the_look_serializer = ComboOfferSerializer(shop_the_look_offers, many=True)

        return Response(data=
            {
                "message": "Offers retrieved successfully",
                "data": {
                    "combo_offers": combo_serializer.data,
                    "shop_the_look": shop_the_look_serializer.data
                }
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"message": "An error occurred while retrieving offers", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
def combo_offer_detail(request, pk):
    """
    Retrieve a specific combo offer by ID.
    """
    try:
        offer = ComboOffer.objects.get(id=pk, is_active=True)

        serializer = ComboOfferSerializer(offer)
        return Response(
            {"message": "Combo offer retrieved successfully", "data": {"combo_offer": serializer.data}},
            status=status.HTTP_200_OK
        )

    except ComboOffer.DoesNotExist:
        return Response(
            {"message": "Combo offer not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return Response(
            {"message": "An error occurred while retrieving the combo offer", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
