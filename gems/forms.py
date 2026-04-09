from django import forms
from .models import Gem, OpenCall, Application


class GemProfileForm(forms.ModelForm):
    class Meta:
        model = Gem
        fields = ['stage_name', 'category', 'bio', 'city', 'cover_image_url', 'profile_image_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(),
        }


class OpenCallForm(forms.ModelForm):
    class Meta:
        model = OpenCall
        fields = ['title', 'description', 'budget', 'category', 'city', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell them why you are the perfect fit...'}),
        }
