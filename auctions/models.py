from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    pass

class Profile(models.Model):
    # Technique for extending Django User Model taken from
    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    watchlist = models.SmallIntegerField(null=True, blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Listing(models.Model):
    #  category syntax taken from https://docs.djangoproject.com/en/3.0/ref/models/fields/
    FASHION = 'FN'
    HEALTH = 'HB'
    TOYS = 'TY'
    BOOKS = 'BK'
    FOOD = 'FD'
    TECHNOLOGY = 'TK'
    HOME = 'HM'
    GIFTS = 'GF'
    AUTO = 'AT'
    OTHER = 'OT'
    CATEGORY_CHOICES = [
        (FASHION, 'Fashion, Clothing & Accessories'),
        (HEALTH, 'Health & Beauty'),
        (TOYS, 'Toys & Baby Equipment'),
        (BOOKS, 'Books, Vinyl and Other Physical Media'),
        (FOOD, 'Groceries, Food and Drinks'),
        (TECHNOLOGY, 'Technology including Phones and Laptops'),
        (HOME, 'Home and Furniture'),
        (GIFTS, 'Flowers and Gifts'),
        (AUTO, 'Vehicles and Automotive'),
        (OTHER, 'Other'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2)
    listed_datetime = models.DateTimeField('date listed')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_URL = models.URLField(max_length=200, blank=True)
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
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment_datetime = models.DateTimeField('date of bid')
    bid = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.listing} - {self.user} - ${self.bid}"
