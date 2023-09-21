from django.contrib import admin

from .models import Post, Category, Location


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'title',
        'text',
        'category',
        'pub_date',
        'author',
        'location',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category', 'location',)
    list_display_links = ('title',)


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'is_published',
        'title',
        'description',
        'slug',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_display_links = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'is_published',
        'name',
        'created_at',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


admin.site.register(Post, PostAdmin)

admin.site.register(Category, CategoryAdmin)

admin.site.register(Location, LocationAdmin)
