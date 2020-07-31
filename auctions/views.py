import datetime
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import User, Listing, Comment, Bid, Watchlist

class NewListingForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Listing Title', 'class': 'form-control'}))
    category = forms.CharField(label="Category", max_length=2, widget=forms.Select(choices = Listing.CATEGORY_CHOICES, attrs={'class': 'form-control'}))
    description = forms.CharField(label="", widget=forms.Textarea(attrs={'placeholder': 'Description', 'class': 'form-control'}))
    starting_bid = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={'placeholder': '0.00', 'class': 'form-control'}))
    image_URL = forms.URLField(label="Image URL", required=False, widget=forms.URLInput(attrs={'placeholder': 'Optional', 'class': 'form-control'}))

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "users": User.objects.all(),
        "comments": Comment.objects.all(),
        "bids": Bid.objects.all()
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=request.POST["first_name"], last_name=request.POST["last_name"])
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def new_listing(request):
    if request.method == "POST":
        # Validate form data.
        new_listing = Listing()
        new_listing_data = NewListingForm(request.POST)
        if new_listing_data.is_valid():
            new_listing.title = new_listing_data.cleaned_data["title"]
            new_listing.description = new_listing_data.cleaned_data["description"]
            new_listing.starting_bid = new_listing_data.cleaned_data["starting_bid"]
            new_listing.image_URL = new_listing_data.cleaned_data["image_URL"]
            new_listing.category = new_listing_data.cleaned_data["category"]
            new_listing.listed_datetime = datetime.datetime.now()
            new_listing.user = request.user

            if len(new_listing.image_URL) == 0:
                new_listing.image_URL = "https://thumbs.dreamstime.com/b/no-image-available-icon-photo-camera-flat-vector-illustration-132483141.jpg"

            new_listing.save()

        # Should I put an else statement here incase form data isn't valid?

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/new_listing.html",{
        "NewListingForm" : NewListingForm()
        })

def display_listing(request, listing_id):
    # Get listing data
    listing = Listing.objects.get(pk=listing_id)

    # Get readable name for category of listing.
    # There must be a better way of doing this but I dont know it.
    for category_list in Listing.CATEGORY_CHOICES:
        if category_list[0] == listing.category:
            listing.category = category_list[1]

    return render(request, "auctions/display_listing.html", {
        "listing": listing
    })

def add_to_watchlist(request, listing_id):

    new_watchlist_item = Watchlist()

    new_watchlist_item.user = request.user

    new_watchlist_item.listing = Listing.objects.get(pk=listing_id)

    try:
        new_watchlist_item.save()
    except IntegrityError:
        messages.error(request, "Item Already in Watchlist")
        print(request.user.watchlist.all())
        return redirect("display_listing", listing_id = listing_id)

    print(request.user.watchlist.all())

# need a way of communicating to the user when an item they are
# trying to add to watchlist is already on there? maybe not
# maybe just redirecting them to a display of watchlist items will
# suffice? in any case need to add remove from watchlist functionality.


    return redirect("display_listing", listing_id = listing_id)
