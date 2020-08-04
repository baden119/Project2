import datetime
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
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
    # Convert watchlist listing id's to a list to send to html
    # This is used to display "add to" or "remove from" watchlist button
    try:
        watchlist_data = request.user.watchlist.all()
    except AttributeError:
            return render(request, "auctions/index.html", {
                "listings": Listing.objects.all()
            })

    watchlist = []
    for item in watchlist_data:
        watchlist.append(item.listing.id)

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "watchlist": watchlist,
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
    # Get listing and bidding data
    listing = Listing.objects.get(pk=listing_id)
    bid_info = Bid.objects.filter(listing=listing_id)
    # If theres no bids, make starting bid ammount the highest current bid.
    if not bid_info:
        highest_bid = listing.starting_bid
    else:
        highest_bid = (bid_info.last().bid)

    # Get readable name for category of listing.
    # There must be a better way of doing this but I dont know it.
    for category_list in Listing.CATEGORY_CHOICES:
        if category_list[0] == listing.category:
            listing.category = category_list[1]

    # Convert watchlist listing id's to a list to send to html
    # This is used to display "add to" or "remove from" watchlist button

    try:
        watchlist_data = request.user.watchlist.all()
    except AttributeError:
            return render(request, "auctions/display_listing.html", {
                "listing": listing,
                "highest_bid": highest_bid,
                "bid_info": bid_info
            })

    watchlist = []
    for item in watchlist_data:
        watchlist.append(item.listing.id)


    return render(request, "auctions/display_listing.html", {
        "listing": listing,
        "watchlist": watchlist,
        "highest_bid": highest_bid,
        "bid_info": bid_info
    })

def add_to_watchlist(request, listing_id):
    # Add item to watchlist.
    new_watchlist_item = Watchlist()
    new_watchlist_item.user = request.user
    new_watchlist_item.listing = Listing.objects.get(pk=listing_id)

    # Make sure item isn't already in user's watchlist
    try:
        new_watchlist_item.save()
    except IntegrityError:
        message = "Item Already in Watchlist"
        return redirect("display_listing", listing_id = listing_id)

    # ADD A SUCCESS MESSAGE TO USER HERE
    return redirect("index")

def remove_from_watchlist(request, listing_id):
    # Remove item from watchlist.
    request.user.watchlist.get(listing_id = listing_id).delete()

    return redirect("index")

def display_watchlist(request):
    # Get watchlist info for current user.
    watchlist_info = request.user.watchlist.all()

    # Watchlist is a relational model, containing only foreign keys (the users id and the listing id)
    # A new list has to be created with the actual listing information to be displayed in html
    # (I think, there might be a better way to do this, i dont know.)
    watchlist = []
    for item in watchlist_info:
        watchlist.append(Listing.objects.get(pk=item.listing_id))

    return render(request, "auctions/display_watchlist.html", {
    "watchlist" : watchlist
    })

def bid(request, listing_id):
    if request.method == "POST":

        new_bid = Bid()
        new_bid.user = request.user
        new_bid.listing = Listing.objects.get(pk=listing_id)
        new_bid.bid_datetime = datetime.datetime.now()
        new_bid.bid = request.POST["bid"]
        new_bid.save()
        print(new_bid)
        print("bid saved")

        # return redirect("index")
        return HttpResponseRedirect(reverse("display_listing", args=(listing_id,)))
