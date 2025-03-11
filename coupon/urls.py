from django.urls import path
from .view.client_side_coupons import AvailableCouponsView, SingleCouponView
from .view.admin_side_coupons import coupon_crud_operation


app_name = 'coupon'

urlpatterns = [
    path('coupons/', AvailableCouponsView.as_view(), name='available-coupons'),
    path('coupons/<int:coupon_id>/', SingleCouponView.as_view(), name='available-coupons'),
    path('admin/coupons/', coupon_crud_operation, name='coupon-get-create'),
    path('admin/coupons/<int:pk>/', coupon_crud_operation, name='coupon-update-delete'),
]