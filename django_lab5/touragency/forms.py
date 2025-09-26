import re
from django import forms
from .models import Review, User
from django.contrib.auth.forms import UserCreationForm

class RegistrationStep1Form(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        return cleaned_data

class RegistrationStep2Form(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'age', 'phone_number', 'address']

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        age = cleaned_data.get('age')
    
        phone_number_pattern = re.compile(r'\+375(25|29|33)\d{7}')
        if phone_number and not re.fullmatch(phone_number_pattern, str(phone_number)):
            self.add_error('phone_number', "Invalid phone number format.")

        if age and (age < 18 or age > 100):
            self.add_error('age', "Age must be between 18 and 100.")

        return cleaned_data

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'age', 'phone_number', 'address', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        age = cleaned_data.get('age')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        # Validate the phone number format
        phone_number_pattern = re.compile(r'\+375(25|29|33)\d{7}')
        if phone_number and not re.fullmatch(phone_number_pattern, str(phone_number)):
            self.add_error('phone_number', "Invalid phone number format.")

        # Validate the age
        if age and (age < 18 or age > 100):
            self.add_error('age', "Age must be between 18 and 100.")

        return cleaned_data
    
class OrderForm(forms.Form):
    amount = forms.IntegerField(min_value=1)
    promocode = forms.CharField(max_length=10, required=False)
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Review
        fields = ['title', 'rating','text']

class ReviewUpdateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']