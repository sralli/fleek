from django.db import models


class BaseModel(models.Model):
    """Base model with timestamps for all models."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class AircraftMeta(BaseModel):
    """Aircraft metadata with detailed specifications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    fin = models.CharField(max_length=20, blank=True)
    sea = models.BooleanField(default=False)
    tmg = models.BooleanField(default=False)
    efis = models.BooleanField(default=False)
    fnpt = models.IntegerField(default=0)
    make = models.CharField(max_length=100)
    run2 = models.BooleanField(default=False)
    aircraft_class = models.IntegerField()
    model = models.CharField(max_length=100)
    power = models.IntegerField(default=1)
    seats = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    kg5700 = models.BooleanField(default=False)
    rating = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=200)
    complex = models.BooleanField(default=False)
    cond_log = models.IntegerField(default=0)
    fav_list = models.BooleanField(default=False)
    category = models.IntegerField()
    high_perf = models.BooleanField(default=False)
    sub_model = models.CharField(max_length=100, blank=True)
    aerobatic = models.BooleanField(default=False)
    ref_search = models.CharField(max_length=20, blank=True)
    reference = models.CharField(max_length=20)
    tailwheel = models.BooleanField(default=False)
    default_app = models.IntegerField(default=0)
    default_log = models.IntegerField(default=2)
    default_ops = models.IntegerField(default=0)
    device_code = models.IntegerField(default=1)
    aircraft_code = models.CharField(max_length=36, blank=True)
    default_launch = models.IntegerField(default=0)
    record_modified = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.make} {self.model} - {self.reference}"
    
    class Meta:
        ordering = ['reference']


class Aircraft(BaseModel):
    """Main aircraft table that references metadata."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    user_id = models.IntegerField()
    table = models.CharField(max_length=50, default="Aircraft")
    guid = models.CharField(max_length=36, unique=True)
    meta = models.OneToOneField(AircraftMeta, on_delete=models.CASCADE, related_name='aircraft')
    platform = models.IntegerField(default=9)
    modified = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.meta.reference} ({self.meta.make} {self.meta.model})"
    
    class Meta:
        ordering = ['meta__reference']
        unique_together = ['user_id', 'guid']


class Airport(BaseModel):
    """Airport/Airfield model with ICAO codes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    icao_code = models.CharField(max_length=4, unique=True)
    iata_code = models.CharField(max_length=3, blank=True)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    source_guid = models.CharField(max_length=36, blank=True, help_text="Original GUID from import source")
    
    def __str__(self):
        return f"{self.icao_code} - {self.name}"
    
    class Meta:
        ordering = ['icao_code']


class CrewMember(BaseModel):
    """Crew member model for flight participants."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.role})" if self.role else self.name
    
    class Meta:
        ordering = ['name']


class Flight(BaseModel):
    """Flight record with detailed logging information."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    user_id = models.IntegerField()
    guid = models.CharField(max_length=36, unique=True)
    flight_date = models.DateField()
    
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, related_name='flights')
    departure = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    arrival = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    
    block_time = models.IntegerField(default=0)
    flight_time = models.IntegerField(default=0)
    instrument_time = models.IntegerField(default=0)
    night_time = models.IntegerField(default=0)
    cross_country_time = models.IntegerField(default=0)
    
    pic_time = models.IntegerField(default=0)
    sic_time = models.IntegerField(default=0)
    dual_time = models.IntegerField(default=0)
    instructor_time = models.IntegerField(default=0)
    
    day_landings = models.IntegerField(default=0)
    night_landings = models.IntegerField(default=0)
    
    crew_members = models.ManyToManyField(CrewMember, blank=True, related_name='flights')
    
    remarks = models.TextField(blank=True)
    route = models.CharField(max_length=500, blank=True)
    
    platform = models.IntegerField(default=9)
    record_modified = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.flight_date} - {self.departure.icao_code} to {self.arrival.icao_code} ({self.aircraft.reference})"
    
    class Meta:
        ordering = ['-flight_date', '-created_at']


def get():
    """Runner function to get all models."""
    models_dict = dict()
    models_dict['BaseModel'] = BaseModel
    models_dict['AircraftMeta'] = AircraftMeta
    models_dict['Aircraft'] = Aircraft
    models_dict['Airport'] = Airport
    models_dict['CrewMember'] = CrewMember
    models_dict['Flight'] = Flight
    return models_dict