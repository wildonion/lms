from django.contrib import admin

# Register your models here.
from tickets.models import Ticket

admin.site.register(Ticket)
