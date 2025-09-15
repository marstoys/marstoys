from django.contrib import admin
from django.contrib.auth.models import User, Group
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
# Default User va Group'ni admindan olib tashlash
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)