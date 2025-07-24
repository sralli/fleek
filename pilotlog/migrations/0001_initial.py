# Generated Django migration for PilotLog models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AircraftMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fin', models.CharField(blank=True, max_length=20)),
                ('sea', models.BooleanField(default=False)),
                ('tmg', models.BooleanField(default=False)),
                ('efis', models.BooleanField(default=False)),
                ('fnpt', models.IntegerField(default=0)),
                ('make', models.CharField(max_length=100)),
                ('run2', models.BooleanField(default=False)),
                ('aircraft_class', models.IntegerField()),
                ('model', models.CharField(max_length=100)),
                ('power', models.IntegerField(default=1)),
                ('seats', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('kg5700', models.BooleanField(default=False)),
                ('rating', models.CharField(blank=True, max_length=100)),
                ('company', models.CharField(max_length=200)),
                ('complex', models.BooleanField(default=False)),
                ('cond_log', models.IntegerField(default=0)),
                ('fav_list', models.BooleanField(default=False)),
                ('category', models.IntegerField()),
                ('high_perf', models.BooleanField(default=False)),
                ('sub_model', models.CharField(blank=True, max_length=100)),
                ('aerobatic', models.BooleanField(default=False)),
                ('ref_search', models.CharField(blank=True, max_length=20)),
                ('reference', models.CharField(max_length=20)),
                ('tailwheel', models.BooleanField(default=False)),
                ('default_app', models.IntegerField(default=0)),
                ('default_log', models.IntegerField(default=2)),
                ('default_ops', models.IntegerField(default=0)),
                ('device_code', models.IntegerField(default=1)),
                ('aircraft_code', models.CharField(blank=True, max_length=36)),
                ('default_launch', models.IntegerField(default=0)),
                ('record_modified', models.BigIntegerField()),
            ],
            options={
                'ordering': ['reference'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Aircraft',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.IntegerField()),
                ('table', models.CharField(default='Aircraft', max_length=50)),
                ('guid', models.CharField(max_length=36, unique=True)),
                ('platform', models.IntegerField(default=9)),
                ('modified', models.BigIntegerField()),
                ('meta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='aircraft', to='pilotlog.aircraftmeta')),
            ],
            options={
                'ordering': ['meta__reference'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('icao_code', models.CharField(max_length=4, unique=True)),
                ('iata_code', models.CharField(blank=True, max_length=3)),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True)),
            ],
            options={
                'ordering': ['icao_code'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CrewMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('license_number', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.IntegerField()),
                ('guid', models.CharField(max_length=36, unique=True)),
                ('flight_date', models.DateField()),
                ('block_time', models.IntegerField(default=0)),
                ('flight_time', models.IntegerField(default=0)),
                ('instrument_time', models.IntegerField(default=0)),
                ('night_time', models.IntegerField(default=0)),
                ('cross_country_time', models.IntegerField(default=0)),
                ('pic_time', models.IntegerField(default=0)),
                ('sic_time', models.IntegerField(default=0)),
                ('dual_time', models.IntegerField(default=0)),
                ('instructor_time', models.IntegerField(default=0)),
                ('day_landings', models.IntegerField(default=0)),
                ('night_landings', models.IntegerField(default=0)),
                ('remarks', models.TextField(blank=True)),
                ('route', models.CharField(blank=True, max_length=500)),
                ('platform', models.IntegerField(default=9)),
                ('record_modified', models.BigIntegerField()),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flights', to='pilotlog.aircraft')),
                ('arrival', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arrivals', to='pilotlog.airport')),
                ('crew_members', models.ManyToManyField(blank=True, related_name='flights', to='pilotlog.CrewMember')),
                ('departure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departures', to='pilotlog.airport')),
            ],
            options={
                'ordering': ['-flight_date', '-created_at'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='aircraft',
            unique_together={('user_id', 'guid')},
        ),
    ] 