from django.contrib import admin
from .models import Caveau, Defunt, Reservation, Concession, Exhumation

admin.site.register(Caveau)
admin.site.register(Defunt)
admin.site.register(Reservation)
admin.site.register(Concession)
admin.site.register(Exhumation)