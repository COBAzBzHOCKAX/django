from django.contrib import admin

from .models import Category, Product, Material, ProductMaterial


def nullfy_quantity(modeladmin, request, queryset):
    queryset.update(quantity=0)
nullfy_quantity.short_description = 'Обнулить товары (как срок президента в 2020-м)'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'quantity', 'category', 'price', 'on_stock')
    list_filter = ('name', 'description', 'quantity', 'price', 'category')
    search_fields = ('name', 'description', 'category__name')
    actions = [nullfy_quantity]


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Material)
admin.site.register(ProductMaterial)

