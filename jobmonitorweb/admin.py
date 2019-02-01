from django.contrib import admin

from .models import Param
from .models import Monitor
from .models import MonitorLog


class ParamAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'description')
    search_fields = ('code', 'value', 'description')
    list_filter = ('code',)


class MonitorAdmin(admin.ModelAdmin):
    list_display = ('title', 'monitor_class', 'is_active', 'task_id')
    search_fields = ('title', )


class MonitorLogAdmin(admin.ModelAdmin):
    list_display = ('monitor', 'message', 'created_at')
    search_fields = ('message', )
    list_filter = ('monitor',)


admin.site.register(Param, ParamAdmin)
admin.site.register(Monitor, MonitorAdmin)
admin.site.register(MonitorLog, MonitorLogAdmin)
