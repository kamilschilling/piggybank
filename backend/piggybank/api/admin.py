from django.contrib import admin
from .models import *

admin.site.register(Child)
admin.site.register(Parent)
admin.site.register(Credit)
admin.site.register(AccountHistory)
admin.site.register(PocketMoney)

