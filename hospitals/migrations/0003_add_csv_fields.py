# Generated manually to add CSV fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0002_add_approval_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospitalprofile',
            name='hospital_category',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='hospital_care_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='discipline_systems',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='specialties',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='facilities',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='accreditation',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='registration_number',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='established_year',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='total_beds',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='number_doctors',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='emergency_services',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='tariff_range',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='bloodbank_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='nodal_person',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='nodal_person_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='nodal_person_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='town',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='subtown',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='village',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='state_id',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='hospitalprofile',
            name='district_id',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
