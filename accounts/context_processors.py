# yourapp/context_processors.py

from .models import Wishlist

def wishlist_count(request):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(customer__user=request.user).first()
        count = wishlist.products.count() if wishlist else 0
    else:
        count = 0
    return {'wishlist_count': count}
