from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )

    empty_value_display = '-пусто-'
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
        'slug',
    )

    empty_value_display = '-пусто-'
    search_fields = ('title', 'slug', 'description')


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'post',
        'text',
        'created'
    )

    empty_value_display = '-пусто-'
    search_fields = ('author', 'post', 'text', 'created')


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'user',
    )

    empty_value_display = '-пусто-'
    search_fields = ('author', 'user')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
