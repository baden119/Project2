from auctions.models import Listing


# Taken from https://dev.to/harveyhalwin/using-context-processor-in-django-to-create-dynamic-footer-45k4
def get_category_choices_context(request):

    return {'categories_list': Listing.CATEGORY_CHOICES}
