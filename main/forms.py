from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ChatForm(forms.Form):
    text_field = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control chat-input','placeholder':'What do you want to do?'}), required=True, )

# forms.py
from django import forms

# forms.py
from django import forms


class WorldBuildingFormular(forms.Form):
    RASSEN = [
        ('mensch', 'Mensch'),
        ('zwerg', 'Zwerg'),
        ('elfe', 'Elfe'),
        ('dirnenspruessling', 'Dirnensprüssling'),
        ('hurensohn', 'Hurensohn'),
    ]
    GESCHLECHTER = [
        ('maennlich', 'Männlich'),
        ('weiblich', 'Weiblich'),
        ('divers', 'Etc..'),
    ]
    KAMPF = [
        ('schwert', 'Schwert'),
        ('magie', 'Magie'),
        ('bogen', 'Pfeil und Bogen'),
        ('lanze', 'Lanze'),
    ]

    name = forms.CharField(label="Name", max_length=100, widget=forms.TextInput(attrs={'class': 'input'}))
    rasse = forms.ChoiceField(label="Rasse", choices=RASSEN, widget=forms.RadioSelect(attrs={'class': 'radio'}))
    geschlecht = forms.ChoiceField(label="Geschlecht", choices=GESCHLECHTER,
                                   widget=forms.RadioSelect(attrs={'class': 'radio'}))
    kampf = forms.ChoiceField(label="Kampfstil", choices=KAMPF, widget=forms.RadioSelect(attrs={'class': 'radio'}))
    charakterbeschreibung = forms.CharField(label="Charakterbeschreibung",
                                            widget=forms.Textarea(attrs={'class': 'textarea'}))
    weltbeschreibung = forms.CharField(label="Weltbeschreibung", widget=forms.Textarea(attrs={'class': 'textarea'}))


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

