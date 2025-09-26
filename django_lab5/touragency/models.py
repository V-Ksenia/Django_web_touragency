import datetime
import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django.utils import timezone
import logging

from tzlocal import get_localzone_name

logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

class User(AbstractUser):
    STATUS_CHOICES = (
        ("staff", "staff"),
        ("client", "client"),
    )
    status = models.CharField(choices=STATUS_CHOICES, default="client", max_length=6)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()
    
    timezone = get_localzone_name()

    def save(self, *args, **kwargs):
        phone_number_pattern = re.compile(r'\+375(25|29|33)\d{7}')
        if not re.fullmatch(phone_number_pattern, str(self.phone_number)) or self.age < 18 or self.age > 100:

            logging.exception(f"ValidationError, {self.phone_number} is in incorrect format OR 18 < {self.age} < 100")

            raise ValidationError("Error while creating user (Check phone number and age!)")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name
    

class Climate(models.Model):
    climate = models.CharField(max_length=255)
    
    def __str__(self):
        return self.climate

class Country(models.Model):
    name = models.CharField(max_length=255)
    climate = models.ManyToManyField(Climate, related_name='countries')

    def __str__(self):
        return self.name


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    STAR_CHOICES = (
        (1, "Terrible"),
        (2, "Poor"),
        (3, "Average"),
        (4, "Very Good"),
        (5, "Excellent"),
    )
    stars = models.PositiveSmallIntegerField(choices=STAR_CHOICES, default=3)
    price_per_night = models.PositiveSmallIntegerField()
    country = models.ForeignKey(Country, related_name="hotels", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Tour(models.Model):
    name = models.CharField(max_length=255)
    DURATION_CHOICES = (
        (1, "One week"),
        (2, "Two weeks"),
        (4, "Four weeks"),
    )
    duration = models.IntegerField(choices=DURATION_CHOICES)
    trips = models.PositiveSmallIntegerField()

    hotel = models.ForeignKey(Hotel, related_name="tours", on_delete=models.CASCADE)
    country = models.ForeignKey(Country, related_name="tours", on_delete=models.CASCADE)

    price = models.PositiveIntegerField(default=1)

    photo = models.ImageField(upload_to='images/')
    description = models.TextField()

    def get_price(self):
        self.price = self.hotel.price_per_night * int(self.duration * 7)
        self.save()
        return self.price
    
    def save(self, *args, **kwargs):
        self.price = self.hotel.price_per_night * int(self.duration * 7)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Order(models.Model): 
    number = models.AutoField(primary_key=True)    
    amount = models.PositiveSmallIntegerField(default=1)
    price = models.FloatField()
    departure_date = models.DateField()

    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, related_name='orders', on_delete=models.CASCADE)

    date = models.DateField()

    def use_discount(self, promocode):
        if UsedDiscounts.objects.filter(promocode_id=promocode, user_id=self.user).exists():
            return
        self.price *= (100 - promocode.discount) / 100
        self.save()

        UsedDiscounts.objects.create(promocode=promocode, user=self.user)

    def save(self, *args, **kwargs):
        departure_date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

        self.date = datetime.date.today()

        if not re.fullmatch(departure_date_pattern, str(self.departure_date)):
            logging.exception(f"ValidationError: {self.departure_date} is in incorrect format")
            raise ValidationError("Error while creating order (Check departure date format!)")

        if self.departure_date < datetime.date.today() + datetime.timedelta(days=5):
            logging.exception(f"ValidationError: {self.departure_date} is too soon")
            raise ValidationError("Error while creating order (Departure date must be at least 5 days from today!)")
        
        super().save(*args, **kwargs)

class UsedDiscounts(models.Model):
    promocode = models.ForeignKey('Promocode', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Promocode(models.Model):
    code = models.CharField(max_length=10)
    discount = models.PositiveSmallIntegerField()


#ADDITIONAL PAGES

class Article(models.Model):
    title = models.TextField(max_length=120)
    content = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)


class CompanyInfo(models.Model):
    text = models.TextField()
    logo = models.ImageField(upload_to='images/')


class Partners(models.Model):
    title = models.TextField()
    logo = models.ImageField(upload_to='images/')
    link = models.URLField(max_length=200)


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    date = models.DateField(auto_now_add=True)


class Contact(models.Model):
    description = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images/')


class Vacancy(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()


class Review(models.Model):
    title = models.CharField(max_length=100)
    rating = models.IntegerField()
    text = models.TextField()
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)