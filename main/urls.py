"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('product/',include('product.urls')),
    path('attribute/',include('attribute.urls')),
    path('category/',include('category.urls')),
    path('order/',include('order.urls')),
    path('promotion/',include('promotion.urls')),
    path('store/',include('store.urls')),
    path('franchise/',include('franchise.urls')),
    path('contact/',include('contact.urls')),
    path('carrier/',include('carrier.urls')),
    path('services/',include('services.urls')),
    path('coupon/',include('coupon.urls')),
    path('blog/',include('blog.urls')),
    path('tracking/', include('tracking.urls')),
    path('combo/', include('combo.urls')),
    path('filters/', include('filter.urls')),
    path('dealOfTheWeek/', include(('dealoftheweek.urls'))),
    path('btcoins/', include('btcoins.urls')),
    path('wallet/', include('wallet.urls')),
    path('tracking/', include('tracking.urls')),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
