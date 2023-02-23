# Generated by Django 3.1.7 on 2021-12-25 22:17

from django.db import migrations, models
import django.db.models.deletion
import root.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dealer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Governorate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=20)),
                ('name_en', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ['name_ar'],
            },
        ),
        migrations.CreateModel(
            name='PropertyOutlook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=20)),
                ('name_en', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=20)),
                ('name_en', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ar', models.CharField(max_length=20)),
                ('name_en', models.CharField(max_length=20)),
                ('governorate', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='area_governorate', to='public.governorate')),
            ],
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=400, validators=[root.validators.validate_min_text])),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('dealer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deals', to='dealer.dealer')),
                ('property_area', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='public.propertyarea')),
                ('property_outlook', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='public.propertyoutlook')),
                ('property_type', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='public.propertytype')),
            ],
        ),
    ]