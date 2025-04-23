from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from tablib import Dataset
from product.models import Product, MainProduct
import tempfile
from import_export import resources, fields
from django.http import HttpResponse
from import_export.formats.base_formats import XLSX
from import_export.widgets import ForeignKeyWidget
from attribute.models import Size, Planter, PlanterSize, Color, Weight, Litre
from account.permissions import IsStaffUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class ProductResource(resources.ModelResource):
    product_id = fields.Field(
        column_name='main_product',
        attribute='product_id',
        widget=ForeignKeyWidget(MainProduct, 'name')
    )
    size_id = fields.Field(
        column_name='size',
        attribute='size_id',
        widget=ForeignKeyWidget(Size, 'name')  # or 'size' if preferred
    )
    planter_id = fields.Field(
        column_name='planter',
        attribute='planter_id',
        widget=ForeignKeyWidget(Planter, 'name')
    )
    planter_size_id = fields.Field(
        column_name='planter_size',
        attribute='planter_size_id',
        widget=ForeignKeyWidget(PlanterSize, 'name')
    )
    color_id = fields.Field(
        column_name='color',
        attribute='color_id',
        widget=ForeignKeyWidget(Color, 'color_name')
    )
    weight_id = fields.Field(
        column_name='weight',
        attribute='weight_id',
        widget=ForeignKeyWidget(Weight, 'size_grams')
    )
    litre_id = fields.Field(
        column_name='litre',
        attribute='litre_id',
        widget=ForeignKeyWidget(Litre, 'name')
    )

    class Meta:
        model = Product
        import_id_fields = ('sku',)
        fields = (
            'id', 'product_id', 'name', 'sku', 'stock', 'mrp',
            'size_id', 'planter_id', 'planter_size_id', 'color_id', 'weight_id', 'litre_id',
            'selling_price', 'discount', 'profit', 'cost',
            'visible_online', 'is_default'
        )
    def dehydrate_visible_online(self, obj):
        return 'True' if obj.visible_online else 'False'

    def dehydrate_is_default(self, obj):
        return 'True' if obj.is_default else 'False'


class ExportProductExcelView(APIView):
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]  

    def get(self, request, *args, **kwargs):
        resource = ProductResource()
        dataset = resource.export()
        xlsx_format = XLSX()

        export_data = xlsx_format.export_data(dataset)

        response = HttpResponse(export_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'
        return response


class ImportProductExcelView(APIView):
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]    
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        data = file.read()
        imported_data = Dataset().load(data, format='xlsx')

        resource = ProductResource()
        result = resource.import_data(imported_data, dry_run=True)

        if not result.has_errors():
            resource.import_data(imported_data, dry_run=False)
            return Response({'message': 'Products imported successfully'})
        else:
            error_details = []
            for i, row in enumerate(result.row_errors()):
                row_num, errors = row
                error_details.append({
                    "row": row_num,
                    "errors": [str(error.error) for error in errors]
                })
            return Response({'error': 'Import failed', 'details': error_details}, status=400)