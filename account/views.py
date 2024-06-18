from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from account.forms import CreatorSignupForm, SupporterSignupForm, ChangePasswordForm, EditProfileForm, WithdrawForm
from account.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum

from account.models import Profile, PeopleList
from tier.models import Tier, Subscription
from post.models import PostFileContent, Post

from account.forms import NewListForm

from django.db import transaction
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from django.core.paginator import Paginator

from django.urls import resolve
from django.db.models import Q
from django.core.mail import send_mail
from .forms import ContactForm


# Create your views here.

def SideNavInfo(request):
	user = request.user
	nav_profile = None
	fans = None
	follows = None

	if user.is_authenticated:
		nav_profile = Profile.objects.get(user=user)
		fans = Subscription.objects.filter(subscribed=user).count()
		follows = Subscription.objects.filter(subscriber=user).count()
	
	return {'nav_profile': nav_profile, 'fans': fans, 'follows': follows}


def UserProfile(request, username):
	user = get_object_or_404(User, username=username)
	profile = Profile.objects.get(user=user)
	url = request.resolver_match.url_name

	tiers = None
	no_a_subscriber = None
	posts = None
	page_type = None
	posts_data = None

	if request.user != user:
		try:
			#Check if the user is subscribed to the profile
			subscriber_tier = Subscription.objects.get(subscriber=request.user, subscribed=user, expired=False)
			#Then we get the tiers of the profile and exclude the tiers that we are currently subscribed
			tiers = Tier.objects.filter(user=user).exclude(number=subscriber_tier.tier.number)
			if url == 'profilephotos':
				posts = PostFileContent.objects.filter(user=user, tier__number__lte=subscriber_tier.tier.number).order_by('-posted').exclude(file__endswith='mp4')
				page_type = 1
			elif url == 'profilevideos':
				posts = PostFileContent.objects.filter(user=user, tier__number__lte=subscriber_tier.tier.number).order_by('-posted').exclude(file__endswith='jpg')
				page_type = 2
			else:
				posts = Post.objects.filter(user=user, tier__number__lte=subscriber_tier.tier.number).order_by('-posted')
				page_type = 3
		except Exception:
			tiers = Tier.objects.filter(user=user)
			no_a_subscriber = False
	else:
		if url == 'profilephotos':
			posts = PostFileContent.objects.filter(user=user).order_by('-posted').exclude(file__endswith='mp4')
			page_type = 1
		elif url == 'profilevideos':
			posts = PostFileContent.objects.filter(user=user).order_by('-posted').exclude(file__endswith='jpg')
			page_type = 2
		else:
			posts = Post.objects.filter(user=user).order_by('-posted')
			page_type = 3
	
	#Pagination
	if posts:
		paginator = Paginator(posts, 6)
		page_number = request.GET.get('page')
		posts_data = paginator.get_page(page_number)
	
	#Profile stats
	income = Subscription.objects.filter(subscribed=user, expired=False).aggregate(Sum('tier__price'))
	fans_count = Subscription.objects.filter(subscribed=user, expired=False).count()
	posts_count = Post.objects.filter(user=user).count()


	#Favorite people lists select
	favorite_list = PeopleList.objects.filter(user=request.user)

	#Check if the profile is in any of favorite list
	person_in_list = PeopleList.objects.filter(user=request.user, people=user).exists()

	#New Favorite List form
	if request.method == 'POST':
		form = NewListForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			PeopleList.objects.create(title=title, user=request.user)
			return HttpResponseRedirect(reverse('profile', args=[username]))
	else:
		form = NewListForm()

	template = loader.get_template('profile.html')

	context = {
		'profile':profile,
		'tiers': tiers,
		'form': form,
		'favorite_list': favorite_list,
		'person_in_list': person_in_list,
		'posts': posts_data,
		'page_type': page_type,
		'income': income,
		'fans_count': fans_count,
		'posts_count': posts_count,
		'no_a_subscriber': no_a_subscriber,

	}

	return HttpResponse(template.render(context, request))

def SupporterSignup(request):
	if request.method == 'POST':
		form = SupporterSignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, password=password, is_supporter=True)
			return redirect('edit-profile')
	else:
		form = SupporterSignupForm()
	
	context = {
		'form':form,
	}

	return render(request, 'registration/supporter_signup.html', context)

def CreatorSignup(request):
	if request.method == 'POST':
		form = CreatorSignupForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			User.objects.create_user(username=username, email=email, password=password, is_creator=True)
			return redirect('edit-profile')
	else:
		form = CreatorSignupForm()
	
	context = {
		'form':form,
	}

	return render(request, 'registration/creator_signup.html', context)


@login_required
def PasswordChange(request):
	user = request.user
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			new_password = form.cleaned_data.get('new_password')
			user.set_password(new_password)
			user.save()
			update_session_auth_hash(request, user)
			return redirect('change_password_done')
	else:
		form = ChangePasswordForm(instance=user)

	context = {
		'form':form,
	}

	return render(request, 'registration/change_password.html', context)

def PasswordChangeDone(request):
	return render(request, 'change_password_done.html')

'''def PasswordChange(request):
    if request.method == 'POST':
        # If the email form was submitted, generate an OTP and send it to the email address
        email_form = PasswordResetFormWithEmail(request.POST)
        if email_form.is_valid():
            email = email_form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Generate OTP and store it in session
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['reset_user_id'] = user.id

            # Send OTP to user's email
            subject = 'OTP Verification'
            message = f'Your OTP is {otp}.'
            from_email = settings.EMAIL_HOST_USER
            to_email = email
            send_mail(subject, message, from_email, [to_email])

            return redirect('verify_otp')

        # If the OTP verification form was submitted, verify the OTP and reset the password if valid
        otp_form = OTPVerificationForm(request.POST)
        if otp_form.is_valid():
            otp = otp_form.cleaned_data['otp']
            if otp == request.session.get('otp'):
                user_id = request.session.get('reset_user_id')
                user = User.objects.get(id=user_id)
                new_password = otp_form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                return redirect('password_change_done')

    else:
        email_form = PasswordResetFormWithEmail()
        otp_form = OTPVerificationForm()

    context = {
        'email_form': email_form,
        'otp_form': otp_form,
    }

    return render(request, 'registration/password_change.html', context)

def VerifyOTP(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            user = authenticate(request, otp=otp)
            if user is not None:
                # OTP is valid, login user and redirect
                login(request, user)
                new_password = form.cleaned_data.get('new_password')
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                del request.session['otp']
                return redirect('password_change_done')
            else:
                # Invalid OTP, show error message
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            # Form is invalid, show error message
            messages.error(request, 'Invalid form. Please try again.')
    else:
        form = OTPVerificationForm()

    context = {'form': form}
    return render(request, 'registration/verify_otp.html', context)

def password_change_done(request):
    return render(request, 'registration/password_change_done.html')
'''


@login_required
def EditProfile(request):
	user = request.user.id
	profile = Profile.objects.get(user__id=user)
	user_basic_info = User.objects.get(id=user)

	if request.method == 'POST':
		form = EditProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			profile.picture = form.cleaned_data.get('picture')
			profile.banner = form.cleaned_data.get('banner')
			user_basic_info.first_name = form.cleaned_data.get('first_name')
			user_basic_info.last_name = form.cleaned_data.get('last_name')
			profile.location = form.cleaned_data.get('location')
			profile.url = form.cleaned_data.get('url')
			profile.profile_info = form.cleaned_data.get('profile_info')
			profile.save()
			user_basic_info.save()
			messages.success(request, 'Your profile has been updated!')
	else:
		form = EditProfileForm(instance=profile)

	context = {
		'form':form,
	}

	return render(request, 'registration/edit_profile.html', context)

def addToList(request):
	user = request.user
	if request.method == 'POST':
		to_list = request.POST.get('list_item')
		to_person = request.POST.get('to')
		person = get_object_or_404(User, username=to_person)
		try:
			people_list = get_object_or_404(PeopleList, user=user, id=to_list)
			people_list.people.add(person)
			return HttpResponseRedirect(reverse('profile', args=[to_person]))
		except Exception as e:
			raise e

def RemoveFromList(request, username):
	person = get_object_or_404(User, username=username)
	list_id = PeopleList.objects.get(user=request.user, people=person)
	try:
		PeopleList.people.through.objects.filter(user_id=person.id, peoplelist_id=list_id).delete()
		return HttpResponseRedirect(reverse('profile', args=[person]))
	except Exception as e:
		raise e

def ShowList(request):
	user_lists = PeopleList.objects.filter(user=request.user)

	#New Favorite List form
	if request.method == 'POST':
		form = NewListForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			PeopleList.objects.create(title=title, user=request.user)
			return HttpResponseRedirect(reverse('profile', args=[request.user.username]))
	else:
		form = NewListForm()

	context = {
		'user_lists': user_lists,
		'form': form,
	}

	return render(request, 'user_lists.html', context)

def listpeople(request, list_id):
	user_list = get_object_or_404(PeopleList, id=list_id)

	context = {
		'user_list': user_list,
	}

	return render(request, 'people_list.html', context)

def listpeopledelete(request, list_id):
	PeopleList.objects.filter(id=list_id).delete()
	return HttpResponseRedirect(reverse('show-my-lists'))


def search_users(request):
    query = request.GET.get("q")
    context = {}
    
    if query:
        users = User.objects.filter(is_creator=True).filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        #Pagination
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
        }
    
    template = loader.get_template('search.html')
    
    return HttpResponse(template.render(context, request))

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_mail(
                f'New contact form submission from {name}',
                message,
                email,
                ['info.creatorbase@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, "Thanks for contacting us! We've received your message and will get back to you as soon as possible.")
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def privacy(request):
	return render(request, 'privacy.html')

def PaymentView(request):
    user = request.user
    earnings = Subscription.objects.filter(subscribed=user, expired=False).aggregate(Sum('tier__price'))
    context = {
        'earnings': earnings,
    }
    return render(request, 'creator_payments.html', context)

@login_required
def withdraw(request):
    user = request.user
    subscriptions = Subscription.objects.filter(subscribed=user, expired=False)
    earnings = subscriptions.aggregate(Sum('tier__price'))['tier__price__sum'] or 0
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > earnings:
                messages.error(request, 'The amount you entered is greater than your earnings.')
            else:
                # Here, you would implement code to actually transfer the funds to the user
                messages.success(request, 'Your withdrawal request has been submitted successfully.')
                return redirect('profile')
    else:
        form = WithdrawForm()
    context = {
        'form': form,
        'earnings': earnings
    }
    return render(request, 'withdraw.html', context)