from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from news.models import Category
from subscriptions.models import SubscriptionCategories


@login_required
@csrf_protect
def subscriptions_categories(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            SubscriptionCategories.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            SubscriptionCategories.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            SubscriptionCategories.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('category')
    return render(
        request,
        'subscriptions/subscriptions_categories.html',
        {'categories': categories_with_subscriptions}
    )
