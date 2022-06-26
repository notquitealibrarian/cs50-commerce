from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bid(models.Model):
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    is_start_bid = models.BooleanField()
    bid_owner = models.ForeignKey(User, null = True, on_delete=models.CASCADE, related_name="bid_owner")

class Category(models.Model):
    category_title = models.CharField(max_length=64)
    def __str__(self):
        return self.category_title

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="start_bid")
    image_url = models.TextField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listing_category", null=True, blank=True)
    current_bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="current_bid")
    is_active = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    num_bids = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment_text = models.TextField()

class WatchedListing(models.Model):
    watched_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='watched_listings', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name ='watchlist_owner')