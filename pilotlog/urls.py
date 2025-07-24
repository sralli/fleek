from django.urls import path
from .views import get as get_views

views = get_views()
app_name = 'pilotlog'

urlpatterns = [
    # Direct Functionality Endpoints
    path('api/import/', views['ImportFunctionalityView'].as_view(), name='import_functionality'),
    path('api/export/', views['ExportFunctionalityView'].as_view(), name='export_functionality'),
    path('api/health/', views['HealthFunctionalityView'].as_view(), name='health_functionality'),
]


def get():
    """Runner function to get URL patterns."""
    return urlpatterns 