from auctions.models import Listing


# Taken from https://dev.to/harveyhalwin/using-context-processor-in-django-to-create-dynamic-footer-45k4
def get_category_choices_context(request):

    # categorys = []
    # for choice in Listing.CATEGORY_CHOICES:
    #     categorys.append(choice[1])
    return {
        'categories_list': Listing.CATEGORY_CHOICES
    }
