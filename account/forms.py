from django import forms
from django.contrib.auth.forms import UserCreationForm
from account.models import User
from django.core.exceptions import ValidationError
from account.models import Profile, PeopleList
import string
from django.contrib.auth.forms import PasswordResetForm



def ForbiddenUsers(value):
	forbidden_users = ['admin', 'css', 'js', 'authenticate', 'login', 'logout', 'administrator', 'root',
	'email', 'user', 'join', 'sql', 'static', 'python', 'delete']
	if value.lower() in forbidden_users:
		raise ValidationError('Invalid name for user, this is a reserverd word.')

def InvalidUser(value):
	if '@' in value or '+' in value or '-' in value:
		raise ValidationError('This is an Invalid user, Do not user these chars: @ , - , + ')

def UniqueEmail(value):
	if User.objects.filter(email__iexact=value).exists():
		raise ValidationError('User with this email already exists.')

def UniqueUser(value):
	if User.objects.filter(username__iexact=value).exists():
		raise ValidationError('User with this username already exists.')

	



class SupporterSignupForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(), max_length=30, required=True,)
	email = forms.CharField(widget=forms.EmailInput(), max_length=100, required=True,)
	password = forms.CharField(widget=forms.PasswordInput())
	confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True, label="Confirm your password.")
	is_supporter=True

	class Meta:

		model = User
		fields = ('username', 'email', 'password', 'is_supporter')

	def __init__(self, *args, **kwargs):
		super(SupporterSignupForm, self).__init__(*args, **kwargs)
		self.fields['username'].validators.append(ForbiddenUsers)
		self.fields['username'].validators.append(InvalidUser)
		self.fields['username'].validators.append(UniqueUser)
		self.fields['email'].validators.append(UniqueEmail)

	def clean(self):
		super(SupporterSignupForm, self).clean()
		password = self.cleaned_data.get('password')
		confirm_password = self.cleaned_data.get('confirm_password')

		if password != confirm_password:
			self._errors['password'] = self.error_class(['Passwords do not match. Try again'])
		return self.cleaned_data

class CreatorSignupForm(forms.ModelForm):
	username = forms.CharField(widget=forms.TextInput(), max_length=30, required=True,)
	email = forms.CharField(widget=forms.EmailInput(), max_length=100, required=True,)
	password = forms.CharField(widget=forms.PasswordInput())
	confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True, label="Confirm your password.")
	is_creator=True

	class Meta:

		model = User
		fields = ('username', 'email', 'password', 'is_creator')

	def __init__(self, *args, **kwargs):
		super(CreatorSignupForm, self).__init__(*args, **kwargs)
		self.fields['username'].validators.append(ForbiddenUsers)
		self.fields['username'].validators.append(InvalidUser)
		self.fields['username'].validators.append(UniqueUser)
		self.fields['email'].validators.append(UniqueEmail)

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if len(password) < 8:
			raise forms.ValidationError("Password must be at least 8 characters long")
		if not any(char.isdigit() for char in password):
			raise forms.ValidationError("Password must contain at least one digit")
		if not any(char.isupper() for char in password):
			raise forms.ValidationError("Password must contain at least one uppercase letter")
		if not any(char in string.punctuation for char in password):
			raise forms.ValidationError("Password must contain at least one symbol")		
		return password
	
	def clean(self):
		super().clean()
		password = self.cleaned_data.get('password')
		confirm_password = self.cleaned_data.get('confirm_password')

		if password != confirm_password:
			self.add_error('confirm_password', 'Passwords do not match.')

	'''def clean(self):
		super(CreatorSignupForm, self).clean()
		password = self.cleaned_data.get('password')
		confirm_password = self.cleaned_data.get('confirm_password')

		if password != confirm_password:
			self._errors['password'] = self.error_class(['Passwords do not match. Try again'])
		return self.cleaned_data'''
	

class ChangePasswordForm(forms.ModelForm):
	id = forms.CharField(widget=forms.HiddenInput())
	old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input is-medium'}), label="Old password", required=True)
	new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input is-medium'}), label="New password", required=True)
	confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input is-medium'}), label="Confirm new password", required=True)

	class Meta:
		model = User
		fields = ('id', 'old_password', 'new_password', 'confirm_password')

	def clean(self):
		super(ChangePasswordForm, self).clean()
		id = self.cleaned_data.get('id')
		old_password = self.cleaned_data.get('old_password')
		new_password = self.cleaned_data.get('new_password')
		confirm_password = self.cleaned_data.get('confirm_password')
		user = User.objects.get(pk=id)
		if not user.check_password(old_password):
			self._errors['old_password'] =self.error_class(['Old password do not match.'])
		if new_password != confirm_password:
			self._errors['new_password'] =self.error_class(['Passwords do not match.'])
		return self.cleaned_data
	
class PasswordResetFormWithEmail(PasswordResetForm):
    email = forms.EmailField(label='Email', max_length=254, 
                             widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control'}))

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label='OTP', max_length=6,
                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(label='New password', max_length=128, 
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(label='Confirm new password', max_length=128, 
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')

class EditProfileForm(forms.ModelForm):
	first_name = forms.CharField(widget=forms.TextInput(), max_length=50, required=False)
	last_name = forms.CharField(widget=forms.TextInput(), max_length=50, required=False)
	picture = forms.ImageField(required=False)
	banner = forms.ImageField(required=False)
	location = forms.CharField(widget=forms.TextInput(), max_length=25, required=False)
	url = forms.URLField(widget=forms.TextInput(), max_length=60, required=False)
	profile_info = forms.CharField(widget=forms.TextInput(), max_length=260, required=False)

	class Meta:
		model = Profile
		fields = ('picture', 'banner', 'first_name', 'last_name', 'location', 'url', 'profile_info')

class NewListForm(forms.ModelForm):
	title = forms.CharField(widget=forms.TextInput(), max_length=150, required=True)

	class Meta:
		model = PeopleList
		fields = ('title',)

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

class WithdrawForm(forms.Form):
	amount = forms.FloatField()
