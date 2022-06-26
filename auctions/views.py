from operator import truediv
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from . import models
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, Bid, Category, Listing, Comment, WatchedListing

def index(request):
    listings = models.Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
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

class NewListingForm(forms.Form):
    title = forms.CharField(label="Listing Title")
    description = forms.CharField(widget=forms.Textarea, label="Listing Description")
    start_bid = forms.DecimalField(label = "Starting Bid")
    image_url = forms.CharField(widget=forms.Textarea, label="URL for image (optional)", required=False)
    category = forms.CharField(label="Category (optional)", required=False)

login_required(login_url='/login')
def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = models.Listing()
            if form.cleaned_data['category']:
                category = models.Category()
                category.category_title = form.cleaned_data['category']
                category.save()
                listing.category = category
            bid = models.Bid()
            bid.amount = form.cleaned_data['start_bid']
            bid.is_start_bid = True
            bid.bid_owner = request.user
            bid.save()
            listing.title = form.cleaned_data['title']
            listing.description = form.cleaned_data['description']
            listing.start_bid = bid
            listing.image_url = form.cleaned_data['image_url']
            listing.current_bid = bid
            listing.is_active = True
            listing.owner = request.user
            listing.num_bids = 0
            listing.save()
            return redirect(reverse('listing', args=[listing.pk]))
        else:
            messages.error(request, "Your page is missing vital information.  Ensure all required fields are filled in.")
            return render(request, "auctions/create.html", {
                "create_listing_form": form
            })
    else:
        return render(request, "auctions/create.html", {
        "create_listing_form": NewListingForm()
        })

class BidForm(forms.Form):
    bid = forms.DecimalField(label = "Bid")

@login_required(login_url='/login')
def view_listing(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    catgor = listing.category
    cat_title = catgor.category_title
    user = request.user
    already_watched = models.WatchedListing.objects.filter(owner = user, watched_listing = listing)
    comments = models.Comment.objects.filter(listing = listing)
    if already_watched:
        add_listing = False
    else:
        add_listing = True
    if request.method == "POST":
        form = BidForm(request.POST)
        if (form.is_valid()) and (form.cleaned_data['bid'] > listing.current_bid.amount):
            bid = models.Bid()
            bid.amount = form.cleaned_data['bid']
            bid.bid_owner = request.user
            bid.is_start_bid = False
            bid.save()
            listing.current_bid = bid
            listing.num_bids += 1
            listing.save()
            return redirect(reverse('listing', args=[listing.pk]))
        else:
            messages.error(request, "Your bid doesn't exceed the current and/or starting bid.  Please enter a higher bid.")
            return render(request, "auctions/listing.html", {
                "listing": listing, "bid_form": form
                })
    else:
        form = BidForm()
        return render(request, "auctions/listing.html", {
                "listing": listing, "bid_form": form, "add_listing": add_listing, "comments": comments, "category": cat_title
                })

@login_required(login_url='/login')
def watchlist_view(request):
    listings = models.WatchedListing.objects.filter(owner = request.user)
    return render(request, "auctions/watchlist.html", {"listings": listings})

@login_required(login_url='/login')
def add_to_watchlist(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    user = request.user
    already_watched = models.WatchedListing.objects.filter(owner = user, watched_listing = listing)
    
    if already_watched:
        messages.error(request, "This item is already on your watchlist.")
        return redirect(reverse('listing', args=[listing.pk]))
    else:
        watchlist = WatchedListing()
        watchlist.owner = user
        watchlist.watched_listing = listing
        watchlist.save()
        messages.success(request, "Added to your watchlist!")
        return redirect(reverse('listing', args=[listing.pk]))

@login_required(login_url='/login')
def remove_from_watchlist(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    user = request.user
    already_watched = models.WatchedListing.objects.filter(owner = user, watched_listing = listing)
    if not already_watched:
        messages.error(request, "You can't remove this item from your watchlist, because you haven't watched it yet.")
        return redirect(reverse('listing', args=[listing.pk]))
    else:
        already_watched = models.WatchedListing.objects.filter(owner = user, watched_listing = listing)
        already_watched.delete()
        messages.success(request, "Removed from your watchlist.")
        listings = models.WatchedListing.objects.filter(owner = request.user)
        return render(request, "auctions/watchlist.html", {"listings": listings})

@login_required(login_url='/login')
def close_listing(request, listing_id):
    listing = models.Listing.objects.get(pk=listing_id)
    user = request.user
    if listing.owner == user:
        listing.is_active = False
        listing.save()
    else:
        messages.error(request, "You can't close this listing because you don't own it.")
    return redirect(reverse('listing', args=[listing.pk]))

class NewCommentForm(forms.Form):
    comment_text = forms.CharField(widget=forms.Textarea, label="Comment Text")

@login_required(login_url='/login')
def add_comment(request, listing_id):
    listing = models.Listing.objects.get(pk = listing_id)
    if request.method == "POST":
        form = NewCommentForm(request.POST)
        if form.is_valid():
            comment = models.Comment()
            comment.author = request.user
            comment.listing = listing
            comment.comment_text = form.cleaned_data['comment_text']
            comment.save()
            return redirect(reverse('listing', args=[listing_id]))
        else:
            messages.error(request, "Blank comments are not allowed.  Please enter text or discard your comment.")
            return render(request, "auctions/add_comment.html", {
                "new_comment_form": form
            })
    else:
        return render(request, "auctions/add_comment.html", {
        "new_comment_form": NewCommentForm(), "listing": listing
        })

def view_categories(request):
    categories = models.Category.objects.values('category_title').distinct()
    return render(request, "auctions/categories.html", {"categories": categories})

def view_category(request, category):
    category_object = models.Category.objects.filter(category_title = category)[0]
    title = category_object.category_title
    listings = models.Listing.objects.filter(category__category_title=title)
    return render(request, "auctions/category.html", {"listings": listings, "category": category})