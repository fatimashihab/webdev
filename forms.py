from django import forms

class RegisterForm(forms.Form):
    username=forms.CharField(label="Username")
    firstname=forms.CharField(label="First Name:")
    lastname=forms.CharField(label="Last Name:")
    password1=forms.CharField(label="Password",widget=forms.PasswordInput())
    password2=forms.CharField(label="Confirm Password",widget=forms.PasswordInput())
    email=forms.EmailField(label="Email")

    def clean(self):
        from models import DjUser
        from django.forms.utils import ErrorList
        cleaned_data=super(RegisterForm,self).clean()
        if DjUser.objects.filter(username=cleaned_data["username"]).exists():
            self._errors["username"]=ErrorList(["This username is already taken, try another one"])
        return cleaned_data

class LogInForm(forms.Form):
    username = forms.CharField(label = "Username",widget = forms.TextInput(attrs = {"class":"form-control"}))
    password = forms.CharField(label = "Password", widget = forms.PasswordInput(attrs = {"class":"form-control"}))

class SendUpdates(forms.Form):
    Update= forms.CharField(max_length=250, label="Update")

class SearchUsers(forms.Form):
    Search=forms.CharField(label="Search")
