from django.contrib import admin  # pyright: ignore[reportMissingImports]
from django.urls import path, include # type: ignore from django.urls       pyright: ignore[reportMissingImports]
from django.conf import settings # type: ignore from django.conf
from django.conf.urls.static import static # type: ignore from django.conf.urls.static
from django.shortcuts import redirect # type: ignore from django.shortcuts
from django.http import JsonResponse # type: ignore from django.http
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView # type: ignore from drf_spectacular.views   pyright: ignore[reportMissingImports]


def api_root(request):
    from django.conf import settings as django_settings
    return JsonResponse({
        'name': 'ChurchManager API',
        'version': '1.0.0',
        'description': 'Système de gestion ecclésiastique',
        'endpoints': {
            'documentation': request.build_absolute_uri('/api/docs/'),
            'redoc': request.build_absolute_uri('/api/redoc/'),
            'admin': request.build_absolute_uri('/admin/'),
            'api_v1': request.build_absolute_uri('/api/v1/'),
        },
        'frontend': getattr(django_settings, 'FRONTEND_URL', 'http://localhost:5173'),
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('hierarchy.urls')),
    path('api/v1/', include('members.urls')),
    path('api/v1/', include('contributions.urls')),
    path('api/v1/', include('events.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('reports.urls')),

    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
