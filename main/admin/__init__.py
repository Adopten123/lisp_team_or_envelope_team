from django.contrib import admin

admin.site.site_header = "Цифровой кампус — админпанель"
admin.site.site_title = "Цифровой кампус"
admin.site.index_title = "Управление данными"

from . import inlines
from .university import *
from .people import *
from .learning import *
from .requests_admin import *
from .applicant import *
from .news import *
from .schedule_admin import *
from .notifications import *