from django.shortcuts import render
from rest_framework import generics, status
from ..serializers.project_serializers import ListingSerializer
from ..serializers.notification_serializers import  NotificationSerializer
from ..models import Listing, User, Notification, Attachment, City, Subscription
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Q
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import date, timedelta
import stripe
import os
import numpy as np

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

## Just for filling the DB with dummy data, can be adapted later for actually updating the DB.
class InitDB(APIView):
    today = date.today()
    # Define a get request: frontend asks for stuff
    def post(self, request, format=None):
        
        city = 'London'
        all_listings = []
        for i in range(5):
            listing = { 'city': city,
                        'rent': i * 100,
                        'expected_occupancy': 70,
                        'expected_profit': 1000,
                        'expected_ADR': 100,
                        'break_even_o': 50,
                        'url': f'{i+100}.co.uk',
                        'website': 'Zoopla',
                        'agency_or_host': 'Snack',
                        'address': 'fvnnvdf',
                        'postcode': 'ZHSYSU',
                        'excel_file': f'dd_{i}.xlsx'}
            all_listings.append(listing)
        # import os
        # print(os. getcwd())
        # C:\Users\oscar\OneDrive\Desktop\Real estate\R2SA_app\working_dir_3\R2SA_app\backend-django\backend_v3\backend_v3\
        
        # with open('json_data.json') as json_file:
        #     all_listings = json.load(json_file)
        #     print(all_listings[0])

        # Check if database already has these, if so skip
        city = City(name='London', country ='England', price=200, stripe_subscription_code='price_1MT99MJeYWzBWqCqnYj1zFPZ')
        if not City.objects.filter(name='London').exists():
            city.save()
            city = City.objects.filter(name='London')[0]
        else:
            city = City.objects.filter(name='London')[0]      
        listing_queryset = Listing.objects.filter(city=city)

        # Loop through Listings, load to DB
        if not listing_queryset.exists():
            for i, listing in enumerate(all_listings):
                print(listing)
                # d = Listing(city = True)
                # print(d)
                city = City(name=listing['city'], country ='England')
                if not City.objects.filter(name=listing['city']).exists():
                    city.save()
                    city = City.objects.filter(name=listing['city'])[0]
                else:
                    city = City.objects.filter(name=listing['city'])[0]
                l = Listing(city = city,
                            name = f"Postcode: {listing['postcode']} - Expected profit: {listing['expected_profit']}",
                            rent = f"Rent: {listing['rent']} ppm",
                            breakeven_occupancy = f"Breakeven Occupancy: {listing['break_even_o']}%",
                            description =   f"Expected ADR: {listing['expected_ADR']}; Expected Occupancy: {listing['expected_occupancy']}%; Agency/Host: {listing['agency_or_host']}",
                            comments = '',
                            labels = [f'{i} bed', '1k+ profit'])
                l.save()
                # attachment =    Attachment(name = f'due_diligence_{l.id}',
                #                 src=listing['excel_file'],
                #                 size='1kb',)
                # attachment.save()
                # l.attachments = attachment
                attachment =    Attachment.objects.create(name = f'due_diligence_{l.id}',
                                # src=listing['excel_file'],
                                src=listing['excel_file'],
                                size='1kb',) 
                l.attachments.add(attachment)
                l.expired_date = self.today - timedelta(days=i-2)
                l.url = listing['url']
                l.created_at = self.today - timedelta(days=10) # created 10 days ago
                print('Model instance', l)
                l.save()

        # Save Users to DB  
        # Check if database already has these, if so skip
        my_filter_qs = Q()
        for name in ['Tim', 'Bob']:  
            my_filter_qs = my_filter_qs | Q(username=name)
        user_queryset = User.objects.filter(my_filter_qs)

        # Send the response (the listings we have found that match the user's cities and 
        # authorised listing_ids)
        # if not user_queryset.exists():   
        # london = City(name='London', tags=[])
        # london = City.objects.filter(name='London')[0]
        belfast = City(name='Belfast',country='Ireland', stripe_subscription_code='price_1MTAF7JeYWzBWqCqabe0l1wi')
        if not City.objects.filter(name='Belfast').exists():
            belfast.save()
        # else:
        #     belfast = City.objects.filter(name='Belfast')[0]
        dublin = City(name='Dublin', country='Ireland', stripe_subscription_code='price_1MTAETJeYWzBWqCqN7QY44Et')
        if not City.objects.filter(name='Dublin').exists():
            dublin.save()
        # else:
        #     dublin = City.objects.filter(name='Dublin')[0]

        Bristol = City(name='Bristol', country='England', stripe_subscription_code='price_1MVZsfJeYWzBWqCq2tnfHyMu')
        if not City.objects.filter(name='Bristol').exists():
            Bristol.save()
        # else:
        #     Bristol = City.objects.filter(name='Bristol')[0]

        

        
        if not User.objects.filter(username='Tim').exists():
            tim = User(username='Tim', password='Tim', 
                email='tim@hotmail.com')
            tim.save()
            
        if not User.objects.filter(username='Bob').exists():
            bob =  User(username='Bob', password='Bob',  
                    email='bob@hotmail.com')
            bob.save()

        if not User.objects.filter(username='admin').exists():
            admin = User(username='admin', password='abc',
                email = 'admin@hotmail.com')
            admin.save()

        # Notifications

        # Check if database already has these, if so skip
        notification_queryset = Notification.objects.filter(userName='Tim')
        if not notification_queryset.exists():
            for i in range(3):
                notification = Notification(userName='Tim', description=f'test_{i}')
                notification.save()
            
        return Response(status=status.HTTP_200_OK)
  

class UpdateListings(APIView):
    today = date.today()
    def post(self, request, format=None):

        # If listing is expired, delete. 
        # If recently expired, mark it as expired
        # so doesn't just disappear from frontend
        listing_queryset = Listing.objects.filter()
        for listing in listing_queryset:
            # If expired recently
            if listing.expired_date <= self.today:
                listing.name = 'Listing no longer on the market'
            # If expired more than 3 days ago
            elif listing.expired_date < self.today - timedelta(days=3):
                listing.delete() 
          
        load_and_store_new_listings('London')
        load_and_store_new_listings('Bristol')

        # Add new listings to Users
        for listing in Listing.objects.filter():
            # Runs once a day, should catch all new ones.
            # Although more robust to go through all listings
            if listing.created_at <= self.today:
                # print('Listing:', listing.url, listing.id)
                for user in User.objects.filter(): 
                    if user.profile.cities.filter(name=listing.city.name).exists():
                        print(f'Adding listings to {user.username} leads list')
                        if listing not in user.profile.user_listings.all():
                            # NOTE: need to set listing status to 0 for that user.
                            user.profile.user_listings.add(listing)
                        # if listing.id not in user.profile.authorised_listings_leads:
                        #     if listing.id not in user.profile.authorised_listings_contacted:
                        #         if listing.id not in user.profile.authorised_listings_booked:
                        #             user.profile.authorised_listings_leads.append(listing.id)
                    user.save()
 
        return Response(status=status.HTTP_200_OK)


def load_and_store_new_listings(city):
    # Load new listings
    with open('json_data_' + city + '.json') as json_file:
        all_listings = json.load(json_file)
        # print(all_listings[0])

    # Store in DB if new
    for i, listing in enumerate(all_listings):
        
        city_query = City.objects.filter(name=listing['city'])
        if not city_query.exists():
            city = City(name=listing['city'], country=listing['country'])
            city.save()
        else:
            city = city_query[0]

        bedrooms = listing['bedrooms']
        profit = int(listing['median_income'] - listing['rent'] * 1.3)
        round_profit = np.floor(profit / 1000 )  # profit in 1000's
        
        if round_profit == 0: # If lower than 1000, give profit in 100s
            round_profit = int(np.floor(profit / 100 ))  # profit in 1000's
            labels = [f'{bedrooms} bed', f'{round_profit}00+ profit']
        else:
            labels = [f'{bedrooms} bed', f'{round_profit}k+ profit']

        
        print( f"Postcode: {listing['postcode']} - £{profit}/month")
        
        l = Listing(city = city,
                    name = f"Postcode: {listing['postcode']} - £{profit}/month",
                    rent = f"Rent: {listing['rent']} ppm",
                    description =   f"Expected Occupancy: {int(listing['expected_occupancy'])}%; Agency/Host: {listing['agency_or_host']} - {listing['website']}",
                    comments = '',
                    url = listing['url'],
                    labels = labels )

        if not Listing.objects.filter(url=listing['url']).exists():
            l.save()
            attachment =    Attachment.objects.create(name = f'due_diligence_{l.id}',
                        src=listing['excel_sheet'],
                        size='1kb',)
            attachment.save()
            l.attachments.add(attachment)
        else:
            print('Listing already exists')