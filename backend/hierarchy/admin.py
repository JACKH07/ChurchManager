from django.contrib import admin # type: ignore
from .models import National, Region, District, Paroisse, EgliseLocale


@admin.register(National)
class NationalAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pays', 'date_fondation', 'email']
    search_fields = ['nom', 'pays']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'national', 'responsable']
    list_filter = ['national']
    search_fields = ['nom', 'code']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'region', 'superviseur']
    list_filter = ['region']
    search_fields = ['nom', 'code']


@admin.register(Paroisse)
class ParoisseAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'district', 'chef']
    list_filter = ['district__region']
    search_fields = ['nom', 'code']


@admin.register(EgliseLocale)
class EgliseLocaleAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'paroisse', 'pasteur', 'capacite']
    list_filter = ['paroisse__district__region']
    search_fields = ['nom', 'code']
