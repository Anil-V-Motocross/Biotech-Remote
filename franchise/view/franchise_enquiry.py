from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from franchise.models import FranchiseEnquiry
from franchise.serializers import FranchiseEnquirySerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics

# @csrf_exempt 
# @api_view(['POST'])
# def create_franchise_enquiry(request):
#     """
#     Create a new Franchise Enquiry
#     """
#     serializer = FranchiseEnquirySerializer(data=request.data)
    
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "Franchise Enquiry Created Successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
    
#     return Response({"message": "Validation Error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class FranchiseEnquiryCreateAPIView(generics.CreateAPIView):
    queryset = FranchiseEnquiry.objects.all()
    serializer_class = FranchiseEnquirySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Franchise enquiry submitted successfully!",
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)