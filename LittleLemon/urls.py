from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="LittleLemon Restaurant API",
      default_version='v1',
      description="A REST API for LittleLemon Restaurant",
      contact=openapi.Contact(email="madukapaul92@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')), # Enables login/logout
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('api/', include('LittleLemonAPI.urls')),  # Include app URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'), # schema: drf_yasg
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
