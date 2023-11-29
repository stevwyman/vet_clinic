from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class GatedContent(MiddlewareMixin):
    """
    Prevents specific content directories and types 
    from being exposed to non-authenticated users
    """

    def process_request(self, request):

        path = request.path
        user = request.user # out of the box auth, YMMV

        is_gated = False
        for gated in settings.GATED_CONTENT:
            if path.startswith(gated) or path.endswith(gated):
                is_gated = True
                break

        # Validate the user is an authenticated/valid user
        if is_gated and not user.is_authenticated:
            # Handle redirect
            return HttpResponseRedirect(reverse("home"))
        