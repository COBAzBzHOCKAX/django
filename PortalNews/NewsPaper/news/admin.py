from django.contrib import admin
from subscriptions.tasks import notifier

from .models import Author, Category, Comment, Post, PostCategory


class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_of_creation', 'short_description', 'author', 'type_post', 'post_category')
    list_filter = ('type_post', 'categories__category', 'date_of_creation')
    search_fields = ('title', 'categories__category', 'author__user__username')

    def post_category(self, post):
        return ", ".join(cat.category for cat in post.categories.all())

    model = Post
    inlines = (PostCategoryInline,)

    def save_formset(self, request, form, formset, change):
        if formset.model == PostCategory:
            instances = formset.save(commit=False)

            for instance in instances:
                instance.save()
                notifier.delay(instance.pk)
                break
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)


admin.site.register(Author)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(PostCategory)
