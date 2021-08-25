import re
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from .models import  Menu, UserMenu, GroupMenu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'auth_tree', 'parent', 'icon', 'url',)
    list_display_links = ('name',)
    ordering = ('id',)

    def auth_tree(self, obj):
        user_list = ">".join([x.user.username for x in obj.usermenu_set.all()])
        group_list = ">".join([x.group.name for x in obj.groupmenu_set.all()])
        div = f'<div>{obj.name} [ {user_list}、{group_list}] '
        for i in obj.menu_set.all():
            user_list = ">".join([x.user.username for x in i.usermenu_set.all()])
            group_list = ">".join([x.group.name for x in i.groupmenu_set.all()])
            div += f'<div style="color:#409dfd;margin-left:10px"> > {i.name} ' \
                f'[ {user_list}、{group_list}] </div>'
            for j in i.menu_set.all():
                user_list = ">".join([x.user.username for x in i.usermenu_set.all()])
                group_list = ">".join([x.group.name for x in i.groupmenu_set.all()])
                div += f'<div style="color:skyblue;margin-left:20px"> > {j.name} ' \
                    f'[ {user_list}、{group_list}] </div>'
        return mark_safe(div)

    auth_tree.short_description = '菜单层次'


class UserMenuInline(admin.StackedInline):
    model = UserMenu
    filter_horizontal = ('menu',)
    can_delete = False
    verbose_name_plural = verbose_name = '菜单授权'


class GroupMenuInline(admin.StackedInline):
    model = GroupMenu
    filter_horizontal = ('menu',)
    can_delete = False
    verbose_name_plural = verbose_name = '菜单授权'


class UserAdmin(BaseUserAdmin):
    inlines = (UserMenuInline,)


class GroupAdmin(BaseGroupAdmin):
    inlines = (GroupMenuInline,)


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
