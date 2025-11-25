from django import forms
from .models import Trip

class TripForm(forms.ModelForm): #robie jeden, bo te same pola beda przy update,delete itp, re-używalność ?
    class Meta:
        model = Trip
        fields = ['title', 'destination', 'start_date', 'end_date']
        #owner=automatycznie->ustawić w widoku, participants-> osobno?, created/updated->automatycznie