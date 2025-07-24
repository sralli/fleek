from django.contrib import admin
from .models import Aircraft, AircraftMeta, Airport, CrewMember, Flight


@admin.register(AircraftMeta)
class AircraftMetaAdmin(admin.ModelAdmin):
    list_display = ('reference', 'make', 'model', 'company', 'active')
    list_filter = ('make', 'company', 'active', 'aircraft_class')
    search_fields = ('reference', 'make', 'model', 'ref_search')


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('guid', 'get_reference', 'get_make_model', 'user_id', 'platform')
    list_filter = ('platform', 'table')
    search_fields = ('guid', 'meta__reference', 'meta__make', 'meta__model')
    
    def get_reference(self, obj):
        return obj.meta.reference
    get_reference.short_description = 'Reference'
    
    def get_make_model(self, obj):
        return f"{obj.meta.make} {obj.meta.model}"
    get_make_model.short_description = 'Aircraft'


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('icao_code', 'iata_code', 'name', 'city', 'country')
    list_filter = ('country', 'city')
    search_fields = ('icao_code', 'iata_code', 'name', 'city')


@admin.register(CrewMember)
class CrewMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'license_number')
    list_filter = ('role',)
    search_fields = ('name', 'license_number')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_date', 'get_aircraft', 'departure', 'arrival', 'flight_time', 'pic_time')
    list_filter = ('flight_date', 'aircraft__meta__make', 'departure', 'arrival')
    search_fields = ('guid', 'aircraft__meta__reference', 'departure__icao_code', 'arrival__icao_code')
    date_hierarchy = 'flight_date'
    
    def get_aircraft(self, obj):
        return obj.aircraft.meta.reference
    get_aircraft.short_description = 'Aircraft'
