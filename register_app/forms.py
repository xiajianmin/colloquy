'''
Created on Apr 14, 2013

@author: ACHIRA
'''

from django import forms
from datetime import date
from django.forms import extras

class RegisterForm(forms.Form):
    
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=100)
    
    #first entry is what is send back to the system
    SEX_CHOICES = [('Male','Male'),
                   ('Female','Female'),
                   ('Other','Other')]
    sex = forms.ChoiceField(choices=SEX_CHOICES, widget=forms.RadioSelect())
    
    DOB_START = 1913
    DOB_END = date.today().year - 18
    dob = forms.DateField(widget=extras.SelectDateWidget(years=range(DOB_END,DOB_START,-1)))
    email = forms.EmailField()
    password = forms.CharField(min_length=6, widget=forms.PasswordInput())   

        
        