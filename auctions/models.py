from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    pass

class Listing(models.Model):
    #  category syntax taken from https://docs.djangoproject.com/en/3.0/ref/models/fields/
    FASHION = 'FN'
    HEALTH = 'HB'
    TOYS = 'TY'
    BOOKS = 'BK'
    FOOD = 'FD'
    TECHNOLOGY = 'TK'
    MUSIC = 'MU'
    HOME = 'HM'
    AUTO = 'AT'
    OTHER = 'OT'
    CATEGORY_CHOICES = [
        (FASHION, 'Fashion, Clothing & Accessories'),
        (HEALTH, 'Health & Beauty'),
        (TOYS, 'Toys & Baby Equipment'),
        (BOOKS, 'Books, Vinyl and Other Physical Media'),
        (FOOD, 'Groceries, Food and Drinks'),
        (TECHNOLOGY, 'Technology including Phones and Laptops'),
        (MUSIC, 'Musical Instruments and Accessories'),
        (HOME, 'Home and Furniture'),
        (AUTO, 'Vehicles and Automotive'),
        (OTHER, 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    listed_datetime = models.DateTimeField('date listed')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_URL = models.URLField(blank=True)
    open = models.BooleanField(default = True)
    winner = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, related_name="winner")
    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default = OTHER,
    )

    def __str__(self):
        return f"{self.title}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    comment_datetime = models.DateTimeField('date commented')

    def __str__(self):
        return f"{self.user} - {self.listing} - ({self.comment_datetime.ctime()})"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")
    bid_datetime = models.DateTimeField('date of bid')
    bid = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.listing} - {self.user} - ${self.bid}"

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f" {self.user} - {self.listing}"

    class Meta:
        unique_together = ("user", "listing")
