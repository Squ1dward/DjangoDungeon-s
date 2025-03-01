from django import forms

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ChatForm(forms.Form):
    text_field = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control chat-input','placeholder':'What do you want to do?'}), required=True, )