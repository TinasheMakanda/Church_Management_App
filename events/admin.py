from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Event


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display  = ('title', 'scope', 'status', 'organization', 'start_datetime', 'end_datetime')
    list_filter   = ('scope', 'status', 'organization', 'is_online')
    search_fields = ('title', 'venue_name', 'organization__name')
    raw_id_fields = ('created_by',)
    filter_horizontal = ()

    fieldsets = (
        ('Core',      {'fields': ('organization', 'title', 'description', 'banner', 'status')}),
        ('Scope',     {'fields': ('scope', 'province', 'church')}),
        ('Schedule',  {'fields': ('start_datetime', 'end_datetime')}),
        ('Venue',     {'fields': ('venue_name', 'venue_address', 'is_online', 'stream_url', 'max_attendance')}),
        ('Finance',   {'fields': ('budget', 'finance_metadata'), 'classes': ('collapse',)}),
        ('Meta',      {'fields': ('created_by',), 'classes': ('collapse',)}),
    )
