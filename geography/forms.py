from django import forms
from .models import UserLocation, Region

class UserLocationForm(forms.ModelForm):
    """Form for users to set their location"""
    
    class Meta:
        model = UserLocation
        fields = ['region', 'latitude', 'longitude']
        widgets = {
            'region': forms.Select(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any',
                'placeholder': 'e.g., 33.7490'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': 'any',
                'placeholder': 'e.g., -84.3880'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.all().order_by('name')
        self.fields['region'].empty_label = "Select your region"
        
        # Make latitude and longitude optional
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
