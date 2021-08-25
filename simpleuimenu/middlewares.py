#!/usr/bin/env python
# _*_coding:utf8_*_
#
# middlewares.py
# Created by ShoJinto at 2021/8/9

from django.utils.deprecation import MiddlewareMixin
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from simpleuimenu.models import Menu, GroupMenu, UserMenu


def get_menu_permissions(obj):
    """
    接收request中user对象的id
    :param obj:
    :return: 通过表级联得到user或者user所属group对应的菜单信息
    """
    menu_obj = Menu.objects  # 菜单对象

    umids = [x.id for x in UserMenu.objects.get(user=obj).menu.all()]
    isgroups = [x.id for x in User.objects.get(id=obj).groups.all()]  # 用户所属组
    if isgroups:
        gmids = [[m.id for m in x.menu.all()]
                 for x in GroupMenu.objects.filter(group__in=isgroups)
                 if x.menu.all()][0]  # 获取组被授权的菜单
        menus = menu_obj.filter(Q(id__in=gmids) | Q(id__in=umids))
    else:
        menus = menu_obj.filter(id__in=umids)  # 获取用户被授权的菜单

    return menus


class AuthMenu(MiddlewareMixin):
    """
    基于simpleui的权限控制菜单栏中间件
    """

    def process_request(self, request):
        # 仅处理路径为 /admin/ 的请求，其他路径直接跳过
        if '/admin/' != request.path:
            return
        menus = []  # 定义列表存储最终菜单
        if request.user.is_superuser:
            menu_entity = Menu.objects.all()
        else:
            menu_entity = get_menu_permissions(request.user.id)
        for fields in menu_entity:
            # 设置基础菜单
            menu = fields.base_menu()
            if fields.parent and not request.user.is_superuser:
                menus.append(fields.parents())
            else:
                for child in fields.menu_set.all():
                    menu.setdefault('models', []).append(child.children())

                """
                满足如下条件说明不应该加入菜单列表
                1. (not fields.menu_set.all() and fields.level != 1) 一级目录且没有下级
                2. fields.parent 非一级目录有且下级
                """
                if (not fields.menu_set.all() and fields.level != 1) or fields.parent:
                    continue

                menus.append(menu)


        settings.SIMPLEUI_CONFIG.update({'menus': menus})
