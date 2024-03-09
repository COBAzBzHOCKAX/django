from django.contrib import admin
from subscriptions.tasks import notifier

from .models import Author, Category, Comment, Post, PostCategory


class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1


class PostAdmin(admin.ModelAdmin):
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
