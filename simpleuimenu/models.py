from django.db import models
from django.contrib.auth.models import User, Group


# Create your models here.
class Menu(models.Model):
    MENU_LEVEL = (
        (1, '一级菜单'),
        (2, '二级菜单'),
        (3, '三级菜单'),
    )

    app = models.CharField(verbose_name='app名称', max_length=50, null=True, blank=True)
    name = models.CharField(verbose_name='名称', max_length=50, default='菜单管理', unique=True)
    icon = models.CharField(verbose_name='图标', max_length=50, default='fas fa-user-shield')
    url = models.CharField(verbose_name='路径', max_length=50, null=True, blank=True,
                           default='simpleuimenu/menu/')
    level = models.IntegerField(verbose_name='层级', default=1, choices=MENU_LEVEL)
    parent = models.ForeignKey('self', verbose_name='父菜单', blank=True, null=True,
                               default=0, on_delete=models.CASCADE,
                               help_text='非一级菜单才生效')

    def __str__(self):
        return self.name

    def base_menu(self):
        if not self.url:
            return {'id': self.id, 'name': self.name, 'icon': self.icon}
        return {'id': self.id, 'name': self.name, 'icon': self.icon, 'url': self.url}

    def children(self):
        menu = self.base_menu()
        if self.menu_set:
            for child in self.menu_set.all():
                menu.setdefault('models', []).append(child.base_menu())
        return menu

    def parents(self):
        parent = self.parent
        menu = parent.base_menu()
        menu.setdefault('models', []).append(self.base_menu())
        if parent.parent:
            childtree = menu
            menu = parent.parent.base_menu()
            menu.setdefault('models', []).append(childtree)
        return menu

    class Meta:
        db_table = 'simplemenu'
        verbose_name = '菜单管理'
        verbose_name_plural = '菜单管理'


class UserMenu(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    menu = models.ManyToManyField(Menu, verbose_name='', blank=True)

    def __str__(self):
        return ''

    class Meta:
        db_table = 'simplemenu_user'
        verbose_name = '授权用户'
        verbose_name_plural = '授权用户'


class GroupMenu(models.Model):
    group = models.OneToOneField(Group, null=True, blank=True, on_delete=models.CASCADE)
    menu = models.ManyToManyField(Menu, verbose_name='',blank=True)

    def __str__(self):
        return ''

    class Meta:
        db_table = 'simplemenu_group'
        verbose_name = '授权组'
        verbose_name_plural = '授权组'
