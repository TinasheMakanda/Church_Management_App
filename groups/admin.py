from django.contrib import admin
from .models import ChurchGroup, GroupMembership


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 0
    fields = ('user', 'is_co_leader', 'joined', 'notes')
    raw_id_fields = ('user',)
    readonly_fields = ('joined',)


@admin.register(ChurchGroup)
class ChurchGroupAdmin(admin.ModelAdmin):
    inlines = [GroupMembershipInline]
    list_display  = ('name', 'group_type', 'church', 'leader', 'is_active')
    list_filter   = ('group_type', 'is_active', 'church__province__organization')
    search_fields = ('name', 'church__name')
    raw_id_fields = ('leader',)
    filter_horizontal = ('events',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display  = ('user', 'group', 'is_co_leader', 'joined')
    list_filter   = ('is_co_leader', 'group__church')
    search_fields = ('user__email', 'group__name')
    raw_id_fields = ('user', 'group')
