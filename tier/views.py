from django.shortcuts import render, redirect, get_object_or_404
from tier.forms import NewTierForm

from tier.models import Tier, Subscription
from account.models import User
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
import time

# Create your views here.

@user_passes_test(lambda u: u.is_creator)
def NewTier(request):
    user = request.user

    if request.method == "POST":
        form = NewTierForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            price = form.cleaned_data.get('price')
            can_message = form.cleaned_data.get('can_message')

            Tier.objects.create(title=title, description=description, price=price, user=user, can_message=can_message)
            messages.success(request, 'New Subscription tier has been created!')
    else:
        form = NewTierForm()
    
    context = {
        'form': form,
    }

    return render(request, 'newtier.html', context)


#def Subscribe(request, username, tier_id):
    user = request.user
    subscribing = get_object_or_404(User, username=username)
    tier = Tier.objects.get(id=tier_id)

    try:
        Subscription.objects.get_or_create(subscriber=user, subscribed=subscribing, tier=tier)
        return redirect('index')
    except User.DoesNotExist:
        return redirect('index')

def Subscribe(request, username,tier_id):
    user = request.user
    subscribing = get_object_or_404(User, username=username)
    tier = Tier.objects.get(id=tier_id)
    if request.method == 'POST':
        # Handle payment form submission
        subscription = Subscription(subscriber=user, subscribed=subscribing, tier=tier, paid=True)
        subscription.save()
        messages.success(request, 'Subscription successful!')
        time.sleep(5)  # Wait for 5 seconds before redirecting
        return redirect('index')
    
    else:
        context = {'tier': tier}
        return render(request, 'subscribe.html', context)
    


def FansList(request):
    my_fans = Subscription.objects.filter(subscribed=request.user)

    context = {
        'my_fans': my_fans
    }

    return render(request, 'fans_list.html', context)

def FollowingList(request):
    my_follows = Subscription.objects.filter(subscriber=request.user)

    for follows in my_follows:
        if follows.expired != True:
            end_date = datetime.now() - timedelta(days=30)
            remaining = follows.date.replace(tzinfo=None) - end_date.replace(tzinfo=None)
            days_left = remaining.days
            follows.date = days_left
    
    context = {
        'my_follows': my_follows
    }

    return render(request, 'following_list.html', context)

def CheckExpiration(request):
    exp_date = datetime.now() - timedelta(days=30)
    subs = Subscription.objects.filter(subscriber=request.user, date__lt=exp_date)
    subs.update(expired=True)
    fans = Subscription.objects.filter(subscribed=request.user, date__lt=exp_date)
    fans.update(expired=True)
    return redirect('index')

