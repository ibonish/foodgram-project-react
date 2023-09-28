from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscriptions, User


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'recipes_count',
                    'subs_count')
    list_display_links = ('id', 'username')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return obj.recipes_user.count()

    @admin.display(description='Количество подписчиков')
    def subs_count(self, obj):
        return obj.subscribers.count()


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'user')
    search_fields = ('user__email', 'author__email')
