import datetime
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Comment, Bid

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
            user = User.objects.create_user(username, email, password)
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
