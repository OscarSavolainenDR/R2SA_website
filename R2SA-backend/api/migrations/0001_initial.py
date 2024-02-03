# Generated by Django 4.1.5 on 2023-05-14 17:32

import api.models
from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.CharField(default=api.models.generate_unique_code, max_length=18, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('src', models.CharField(max_length=30)),
                ('size', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Authorised_Listings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('country', models.CharField(max_length=30)),
                ('price', models.IntegerField(default=50)),
                ('description', models.CharField(max_length=200)),
                ('stripe_subscription_code', models.CharField(max_length=40, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.CharField(default=api.models.generate_unique_code, max_length=18, primary_key=True, serialize=False, unique=True)),
                ('postcode', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=1000)),
                ('expected_income', models.IntegerField(default=50)),
                ('profit', models.IntegerField(default=50)),
                ('rent', models.IntegerField(default=50)),
                ('expected_occupancy', models.IntegerField(default=50)),
                ('breakeven_occupancy', models.IntegerField(default=110)),
                ('comments', models.CharField(max_length=250)),
                ('bedrooms', models.IntegerField(default=50)),
                ('labels', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=15), size=None)),
                ('expired_date', models.DateField(default=api.models.Listing.future_date)),
                ('url', models.CharField(max_length=250, null=True, unique=True)),
                ('created_at', models.DateField(default=django.utils.timezone.now)),
                ('excel_sheet', models.IntegerField(default=0)),
                ('attachments', models.ManyToManyField(related_name='attachments_to_listing', to='api.attachment')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.CharField(default=api.models.generate_unique_code_notification, max_length=18, primary_key=True, serialize=False, unique=True)),
                ('userName', models.CharField(max_length=10)),
                ('target', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=50)),
                ('date', models.DateField(auto_now_add=True)),
                ('image', models.ImageField(upload_to='')),
                ('type', models.IntegerField(default=0)),
                ('location', models.CharField(max_length=10)),
                ('locationLabel', models.CharField(max_length=10)),
                ('status', models.CharField(max_length=10)),
                ('readed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(max_length=30)),
                ('sign_up_date', models.DateField(auto_now_add=True)),
                ('authorisations', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), default=api.models.get_list_default, size=None)),
                ('email_confirmed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('key', models.CharField(max_length=32, primary_key=True, serialize=False, unique=True)),
                ('username', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(default=2)),
                ('subscription_date', models.DateField(auto_now_add=True)),
                ('stripe_subscription_id', models.CharField(max_length=40)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.profile')),
            ],
        ),
        migrations.CreateModel(
            name='ResetPassword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=50, unique=True)),
                ('uid', models.CharField(max_length=10, unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='cities',
            field=models.ManyToManyField(through='api.Subscription', to='api.city'),
        ),
        migrations.AddField(
            model_name='profile',
            name='cities_basket',
            field=models.ManyToManyField(related_name='cities_in_basket', through='api.Basket', to='api.city'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='user_listings',
            field=models.ManyToManyField(through='api.Authorised_Listings', to='api.listing'),
        ),
        migrations.CreateModel(
            name='ConfirmEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=50, unique=True)),
                ('uid', models.CharField(max_length=10, unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='basket',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.city'),
        ),
        migrations.AddField(
            model_name='basket',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.profile'),
        ),
        migrations.AddField(
            model_name='authorised_listings',
            name='listing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.listing'),
        ),
        migrations.AddField(
            model_name='authorised_listings',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.profile'),
        ),
    ]