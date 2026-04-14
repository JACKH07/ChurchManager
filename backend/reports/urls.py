from django.urls import path  # pyright: ignore[reportMissingImports]
from .views import DashboardView, RapportFidelesView, RapportFinancierView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('rapports/fideles/', RapportFidelesView.as_view(), name='rapport_fideles'),
    path('rapports/financier/', RapportFinancierView.as_view(), name='rapport_financier'),
]
