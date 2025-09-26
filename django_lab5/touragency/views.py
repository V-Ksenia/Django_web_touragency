import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import *
from django.views import View

import requests

from touragency.forms import *
from .models import *
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth.models import auth
from django.contrib.auth.views import LoginView
import json
import logging

logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

class RegistrationStep1View(View):
    def get(self, request):
        form = RegistrationStep1Form()
        return render(request, 'registration_step1.html', {'form': form})

    def post(self, request):
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            try:
                request.session['username'] = form.cleaned_data['username']
                request.session['password1'] = form.cleaned_data['password1']
                request.session['password2'] = form.cleaned_data['password2']
                return redirect('registration_step2')
            except ValidationError as e:
                form.add_error(None, e.message)
        return render(request, 'registration_step1.html', {'form': form})
    
class RegistrationStep2View(View):
    def get(self, request):
        form = RegistrationStep2Form()
        return render(request, 'registration_step2.html', {'form': form})

    def post(self, request):
        form = RegistrationStep2Form(request.POST)
        if form.is_valid():
            try:
                user = User(
                    username=request.session['username'],
                    password=request.session['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    age=form.cleaned_data['age'],
                    phone_number=form.cleaned_data['phone_number'],
                    address=form.cleaned_data['address'],
                )
                user.set_password(request.session['password1']) 
                user.save()
                return redirect('login')
            except ValidationError as e:
                form.add_error(None, e.message)
        return render(request, 'registration_step2.html', {'form': form})

    
# class UserRegistrationView(View):
#     def get(self, request):
#         form = RegistrationForm()
#         return render(request, 'registration_form.html', {'form': form})

#     def post(self, request):
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             try:
#                 user = form.save(commit=False)
#                 user.set_password(form.cleaned_data['password1'])
#                 user.save()
#                 return redirect('login')
#             except ValidationError as e:
#                 form.add_error(None, e.message)
#         return render(request, 'registration_form.html', {'form': form})

class UserLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login_form.html'

    def get_success_url(self):  
        logging.info("User LOGIN")
        return reverse_lazy('home')
            

class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logging.info(f"{request.user.username} LOGOUT (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            auth.logout(request)
        return redirect('home')


class TourListView(View):
    model = Tour
    queryset = Tour.objects.all()

    def get(self, request, *args, **kwargs):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        hotel_id = request.GET.get('hotel_id')
        country_id = request.GET.get('country_id')
        duration = request.GET.get('duration')

        min_price = int(min_price) if min_price and min_price.isdigit() else None
        max_price = int(max_price) if max_price and max_price.isdigit() else None
        
        countries = Country.objects.all()

        tours = self.filter_tours(min_price, max_price, country_id, hotel_id, duration)
        
        tours_dataa = []

        for tour in tours:
            if tour.trips != 0:
                tours_dataa.append({
                    'id': tour.id,
                    'name': tour.name,
                    'country': tour.country.name,
                    'hotel': tour.hotel.name,
                    'hotel_stars': tour.hotel.stars,
                    'duration_weeks': tour.duration,
                    'price': tour.get_price(),
                    'photo': tour.photo.url,
                })
        tours_data = json.dumps(tours_dataa) 

        return render(request, 'tours.html', {'tours': tours_dataa,'toursjson': tours_data, 'countries': countries})
        #return JsonResponse(tours_data, safe=False)

    @staticmethod
    def filter_tours(min_price=None, max_price=None, country=None, hotel=None, duration=None):
        tours = Tour.objects.all()

        filtered_tours = None

        if hotel:
            tours = tours.filter(hotel=hotel)
        if country:
            tours = tours.filter(country=country)
        if duration:
            tours = tours.filter(duration=duration)

        if min_price is not None and max_price is not None:
            filtered_tours = tours.filter(price__gte=min_price, price__lte=max_price)
        elif min_price is not None:
            filtered_tours = tours.filter(price__gte=min_price)
        elif max_price is not None:
            filtered_tours = tours.filter(price__lte=max_price)

        if filtered_tours is not None:
            return filtered_tours
        return tours


class SpecificTourList(View):
    model = Tour

    def get(self, request, pk, *args, **kwargs):
        tour = Tour.objects.filter(pk=pk)[0]
        tours_dataa = []
        if tour:
            tours_dataa.append({
                'id': tour.id,
                'name': tour.name,
                'country': tour.country.name,
                'country_climate': list(tour.country.climate.all().values_list('climate', flat=True)),
                'hotel': tour.hotel.name,
                'stars_sign': tour.hotel.stars * '★',
                'duration_weeks': tour.duration,
                'price': tour.price,
                'amount_of_trips': tour.trips,
                'description': tour.description,
                'photo': tour.photo.url,
            })
        tours_data = json.dumps(tours_dataa) 
        #return JsonResponse(tours_data, safe=False)
        return render(request, 'specific_tour.html', {'toursjson': tours_data,'tours': tours_dataa})


class HotelListView(View):
    model = Hotel
    queryset = Hotel.objects.all()

    def get(self, request, *args, **kwargs):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        country_id = request.GET.get('country_id')
        stars_value = request.GET.get('stars')

        hotels = self.filter_hotels(min_price, max_price, country_id, stars_value)
        hotels_data = []
        for hotel in hotels:
            hotels_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'stars': hotel.stars,
                'country': hotel.country.name,
                'price_per_night': hotel.price_per_night,
                'stars_sign': hotel.stars * '★'
            })
        #return JsonResponse(hotels_data, safe=False)
        return render(request, 'hotels.html', {'hotels': hotels_data})

    @staticmethod
    def filter_hotels(min_price=None, max_price=None, country=None, stars=None):
        hotels = Hotel.objects.all()

        filtered_hotels = None
        if stars:
            hotels = hotels.filter(stars=stars)
        if country:
            hotels = hotels.filter(country=country)

        if min_price is not None and max_price is not None:
            filtered_hotels = hotels.filter(price_per_night__gte=min_price, price__lte=max_price)
        elif min_price is not None:
            filtered_hotels = hotels.filter(price_per_night__gte=min_price)
        elif max_price is not None:
            filtered_hotels = hotels.filter(price_per_night__lte=max_price)

        if filtered_hotels is not None:
            return filtered_hotels
        return hotels
    

class CountryListView(View):
    def get(self, request, *args, **kwargs):
       
        countries = Country.objects.all()

        countries_data = []
        for country in countries:
            climates = list(country.climate.all().values_list('climate', flat=True))

            countries_data.append({
                'id': country.id,
                'name': country.name,
                'climate': climates,
            })
        #return JsonResponse(countries_data, safe=False)
        return render(request, 'countries.html', {'countries': countries_data})


class UserListView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "staff":
            logging.info(f"{request.user.username} called UserListView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            users = User.objects.filter(status="client")

            users_data = []
            for user in users:
                users_data.append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "age": user.age,
                    "phone_number": user.phone_number,
                })
            #return JsonResponse(users_data, safe=False)
            return render(request, 'users.html', {'users': users_data})
        logging.error(f"{request.user.username} tried to call UserListView (status: {request.user.status})")
        return HttpResponseNotFound("For staff only")


class OrderCreateView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "client" and Tour.objects.filter(pk=pk).exists():
            logging.info(f"{request.user.username} called OrderCreateView | user's Timezone: {request.user.timezone}")
            tour = Tour.objects.get(pk=pk)
            form = OrderForm()
            
            return render(request, 'order_create_form.html', {'form': form, 'tour': tour})
        logging.error(f"Call failed OrderCreateView")
        return redirect('login')
    
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "client":
            tour = Tour.objects.get(pk=pk)
            
            form = OrderForm(request.POST)

            if form.is_valid():
                logging.info(f"OrderForm has no errors")
                
                amount = form.cleaned_data['amount']
                departure_date = form.cleaned_data['departure_date']
                code = form.cleaned_data['promocode']

                promocode = Promocode.objects.filter(code=code).first()

                if amount > tour.trips:
                    logging.warning(f"{amount} is greater than {tour.trips}")
                    return HttpResponse("Check amount of trips")
                else:
                    order = Order.objects.create(user=request.user, tour=tour, amount=amount, price=amount * tour.price, departure_date=departure_date)      
                    
                    if promocode:
                        logging.info(f"Promocode {promocode.code} used by {request.user.username}")
                        order.use_discount(promocode)

                    tour.trips -= amount
                    tour.save()
                    
                    logging.info(f"{tour.name} updated ")

                    url = reverse('user_spec_order', kwargs={"pk": order.user_id, "jk": order.number})
                    return redirect(url)
                
        elif request.user.is_authenticated and request.user.status == "staff":
            logging.error(f"{request.user.username} has status {request.user.status}")
            return HttpResponseNotFound("For clients only")
        else:
            logging.error(f"User is not authenticated")
            return redirect('login')


class UserOrderView(View):
    def get(self, request, pk, *args, **kwargs):

        if request.user.is_authenticated and request.user.id == int(pk):
            logging.info(f"{request.user.username} called UserOrderView | user's Timezone: {request.user.timezone}")
            orders = Order.objects.filter(user_id=pk)

            orders_data = []
            for order in orders:
                orders_data.append({
                    "user": order.user.username,
                    "number": order.number,
                    "tour_name": order.tour.name,
                    "price": order.price,
                    "amount": order.amount,
                    "departure_date": order.departure_date,
                    "creation_date": order.date,
                })

            #return JsonResponse(orders_data, safe=False)
            return render(request, 'user_orders.html', {'orders': orders_data})
        logging.error(f"Call failed UserOrderView")
        return HttpResponseNotFound("Page not found")
    
    
class SpecificOrderView(View):
    def get(self, request, pk, jk, *args, **kwargs):
        if request.user.is_authenticated and request.user.id==int(pk) and Order.objects.filter(user_id=int(pk), number=int(jk)).exists():
            logging.info(f"{request.user.username} called SpecificOrderView | user's Timezone: {request.user.timezone}")

            order = Order.objects.filter(user_id=pk, number=jk).first()

            return render(request, 'order_delete_form.html', {'order': order})
        return HttpResponseNotFound("Page not found")
    
    def post(self, request, pk, jk, *args, **kwargs):
        if request.user.is_authenticated and request.user.id==int(pk) and Order.objects.filter(user_id=int(pk), number=int(jk)).exists():
            order = Order.objects.filter(number=jk, user_id=pk).first()

            order.tour.trips += order.amount
            order.tour.save()
            d = order.number
            order.delete()

            logging.info(f"order number {d} was deleted")

            url = reverse('user_orders', kwargs={"pk": order.user_id})
            return redirect(url)
        logging.error(f"{request.user.username} doesn't own this order")            
        return HttpResponseNotFound("Page not found")
    

class OrderListView(View):
    def get(self, request, *args, **kwargs):      
        if request.user.is_authenticated and request.user.status == "staff":

            logging.info(f"{request.user.username} called OrderListView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            
            orders = Order.objects.all()

            orders_data = []
            for order in orders:
                orders_data.append({
                    "user": order.user.username,
                    "first_name": order.user.first_name,
                    "phone_number": order.user.phone_number,
                    "number": order.number,
                    "tour_name": order.tour.name,
                    "price": order.price,
                    "amount": order.amount,
                    "departure_date": order.departure_date,
                    "creation_date": order.date,
                })
            #return JsonResponse(orders_data, safe=False)
            return render(request, 'user_orders.html', {'orders': orders_data})
        logging.error(f"{request.user.username} has status {request.user.status}") 
        return HttpResponseNotFound("Page not found")


class ReviewCreateView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated and request.user.status == 'client':

            logging.info(f"{request.user.username} called ReviewCreateView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")

            form = ReviewForm()
            return render(request, 'review_create_form.html', {'form': form})
        return redirect('login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == 'client':
            form = ReviewForm(request.POST)
            if form.is_valid():
                logging.info(f"ReviewForm has no errors)")

                title = form.cleaned_data['title']
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']

                review = Review.objects.create(title=title, rating=rating, text=text, user=request.user)
                logging.info(f"Review '{review.title}' was created by {request.user.username} ")
                return redirect('reviews')
        logging.warning("User is not authenticated")
        return redirect('login')


class ReviewEditView(View):
    def get(self, request, pk, jk, *args, **kwargs):
        if request.user.is_authenticated and request.user.id==int(pk) and Review.objects.filter(user_id=int(pk), id=int(jk)).exists():

            logging.info(f"{request.user.username} called ReviewEditView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")

            review = Review.objects.filter(user_id=pk, id=jk).first()
            form = ReviewUpdateForm()
            return render(request, 'review_edit_form.html', {'form': form, 'review': review})
        logging.error(f"Call failed ReviewEditPage")
        return HttpResponseNotFound("Page not found")
     
    def post(self, request, pk, jk, *args, **kwargs):
        if request.user.is_authenticated and request.user.id==int(pk) and Review.objects.filter(user_id=int(pk), id=int(jk)).exists():
            form = ReviewUpdateForm(request.POST)
            if form.is_valid():
                logging.info(f"ReviewForm has no errors)")

                review = Review.objects.filter(user_id=pk, id=jk).first()
                
                text = form.cleaned_data['text']

                review.text = text

                review.save()  

                logging.info(f"Review '{review.title}' was updated by {request.user.username} ") 

                return redirect('reviews')
        logging.warning("User is not authenticated")
        return redirect('login')


#API
class PlaceCoordinates(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            url = "https://opentripmap-places-v1.p.rapidapi.com/en/places/geoname"

            name = str(pk)
            querystring = {"name": name}

            headers = {
            "X-RapidAPI-Key": "cf52fdec52msh3467d0348f8b9a8p15eb7fjsn4a6d39d8974e",
            "X-RapidAPI-Host": "opentripmap-places-v1.p.rapidapi.com"
            }

            response = requests.get(url, headers=headers, params=querystring)
            return JsonResponse(response.json())
        return HttpResponseNotFound("Page not found")
    

def world_languages(request):
    if request.user.is_authenticated:
        url = "https://tourist-attraction.p.rapidapi.com/languages"

        headers = {
        "X-RapidAPI-Key": "cf52fdec52msh3467d0348f8b9a8p15eb7fjsn4a6d39d8974e",
        "X-RapidAPI-Host": "tourist-attraction.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers)  
        return JsonResponse(response.json()) 
    return HttpResponseNotFound("Page not found")



#ADDITIONAL PAGES
def home(request):
    latest_article = Article.objects.latest('date')
    partners = Partners.objects.all()
    tours = Tour.objects.all()
    info = CompanyInfo.objects.first()
    reviews = Review.objects.all()
    tours_data = []
    for tour in tours:
        tours_data.append({
            'id': tour.id,
            'name': tour.name,
            'country': tour.country.name,
            'hotel': tour.hotel.name,
            'duration_weeks': tour.duration,
            'price': tour.get_price(),
            'photo': tour.photo,
        })

    return render(request, 'home.html', {'latest_article': latest_article,
                                         'tours': tours_data,
                                         'partners': partners,
                                         'company_info': info,
                                         'reviews': reviews})

def about_company(request):
    info = CompanyInfo.objects.first()
    return render(request, 'about.html', {'company_info': info})

def news(request):
    news = Article.objects.all().order_by('-date')
    return render(request, 'news.html', {'news': news})

def news_detail(request, pk):
    news = get_object_or_404(Article, id=pk)
    return render(request, 'news_detail.html', {'news': news})

def promocodes(request):
    promocodes = Promocode.objects.all()
    usedpromos = UsedDiscounts.objects.all()
    return render(request, 'promocodes.html', {'promocodes': promocodes,
                                               'usedpromos': usedpromos
                                               })

def faqs(request):
    faqs = FAQ.objects.all()
    return render(request, 'faqs.html', {'faqs': faqs})

def contacts(request):
    contacts = Contact.objects.all()
    contacts_json = []

    for contact in contacts:
        contacts_json.append({
            'id': contact.id,
            'first_name': contact.user.first_name,
            'last_name': contact.user.last_name,
            'phone_number': contact.user.phone_number,
            'email': contact.user.email,
            'description': contact.description,
            'photo': contact.photo.url if contact.photo else None,

        })
    
    return render(request, 'contacts.html', {'contacts': json.dumps(contacts_json)})

def vacancies(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'vacancies.html', {'vacancies': vacancies})

def reviews(request):
    reviews = Review.objects.all()
    return render(request, 'reviews.html', {'reviews': reviews})

def privacy_policy(request):
    return render(request, 'privacy.html')