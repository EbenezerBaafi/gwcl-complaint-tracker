from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['category', 'title', 'description', 'address', 'gps_coordinates', 'image']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Brief title of your complaint'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Describe your complaint in detail...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Your location/address'
            }),
            'gps_coordinates': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Optional: GPS coordinates'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }
        labels = {
            'category': 'Complaint Category',
            'title': 'Title',
            'description': 'Description',
            'address': 'Location/Address',
            'gps_coordinates': 'GPS Coordinates (Optional)',
            'image': 'Upload Image (Optional)'
        }


class ComplaintRatingForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['customer_rating', 'customer_feedback']
        widgets = {
            'customer_rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'customer_feedback': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Share your feedback about how we handled your complaint...'
            })
        }