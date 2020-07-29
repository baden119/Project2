from django.contrib import admin
from .models import User, Listing, Comment, Bid

class ListingAdmin(admin.ModelAdmin):
    list_display = ( "__str__", "description", "category", "starting_bid")

class CommentAdmin(admin.ModelAdmin):
    comment_display = ("__str__")
# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Comment)
admin.site.register(Bid)
