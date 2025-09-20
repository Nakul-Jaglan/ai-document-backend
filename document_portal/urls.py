"""
URL configuration for document_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from documents.views import UserViewSet, DocumentViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.static import serve
from django.http import JsonResponse
from django.utils import timezone

# Add a simple root view to confirm the API is working
def api_root(request):
    return JsonResponse({"message": "API is running. Use /api/ to access endpoints."})

# Add a health check endpoint for uptime monitoring
def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "message": "Backend server is running",
        "timestamp": timezone.now().isoformat()
    })

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', api_root, name='api_root'),  # Add a root path handler
    path('health/', health_check, name='health_check'),  # Health check endpoint
    path('admin/', admin.site.urls),
    path('api/auth/register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
