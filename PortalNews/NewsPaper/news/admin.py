from django.contrib import admin
from .models import Author, Post, Comment, Category, PostCategory


class CategoryInLine(admin.TabularInline):
    model = PostCategory
    extra = 1

class PostAdmin(admin.ModelAdmin):
    model = Post
    inlines = (CategoryInLine,)


admin.site.register(Author)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(PostCategory)