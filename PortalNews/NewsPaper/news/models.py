from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Author(models.Model):
    rating = models.IntegerField(default=0)  # Рейтинг автора

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Ключ к юзеру

    def __str__(self):
        return f'{User.objects.get(pk=self.user.pk)}'

    def update_rating(self):
        posts = Post.objects.filter(author_id=self.pk)
        comments = Comment.objects.filter(user=self.user)

        self.rating = 0
        for post in posts:
            self.rating += post.rating * 3
            post_coments = Comment.objects.filter(post=post)
            for post_comment in post_coments:
                self.rating += post_comment.rating

        for comment in comments:
            self.rating += comment.rating

        self.save()


class Category(models.Model):
    category = models.CharField(max_length=255, unique=True)  # Категории новостей/статей

    def __str__(self):
        return f'{self.category}'


class Post(models.Model):
    class TypePost(models.TextChoices):  # Определение типов постов, формат "Статья" или "Новость"
        article = "ART", _("Статья")
        news = "NWS", _("Новость")

    type_post = models.CharField(max_length=3,  # Тип поста
                                 choices=TypePost.choices,
                                 default=TypePost.news,
                                 )
    date_of_creation = models.DateTimeField(auto_now_add=True)  # Дата и время создания поста
    title = models.CharField(max_length=255)  # Заголовок статьи/новости
    text = models.TextField()  # Текст статьи/новости
    rating = models.IntegerField(default=0)  # Рейтинг статьи/новости

    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # связь мн-к-од с моделью Author
    categories = models.ManyToManyField(Category, through="PostCategory")  # связь мн-к-мн с моделью Category

    def __str__(self):
        return (
            f'{self.date_of_creation.strftime("%Y-%m-%d %H:%M")}  |  '
            f'{self.title}  |  '
            f'Автор: {User.objects.get(pk=self.author.pk)}  |  '
            f'рейтинг: {self.rating}'
        )

    def like(self, x=1):
        self.rating += x
        self.save()

    def dislike(self, x=1):
        self.rating -= x
        self.save()

    def preview(self):
        return f'{self.text[:124]}...'

    def get_absolute_url(self):
        if self.type_post == 'NWS':
            return reverse('news_detail', kwargs={'pk': self.pk})
        elif self.type_post == 'ART':
            return reverse('articles_detail', kwargs={'pk': self.pk})
        else:
            return reverse('posts')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


class PostCategory(models.Model):  # модель для связи мн-к-мн
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.category}  |  {self.post.title}  |  Автор: {User.objects.get(pk=self.post.author.pk)}'


class Comment(models.Model):  # Комментарии под статьёй/новостью
    comment = models.TextField()  # Текст комментария
    date_of_writing = models.DateTimeField(auto_now_add=True)  # Дата написания комментария
    rating = models.IntegerField(default=0)  # Рейтинг комментария

    post = models.ForeignKey(Post, on_delete=models.CASCADE)  # связь мн-к-одн с моделью Post
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # связь мн-к-одн с моделью User

    def like(self, x=1):
        self.rating += x
        self.save()

    def dislike(self, x=1):
        self.rating -= x
        self.save()

    def __str__(self):
        return f'{self.date_of_writing.strftime("%Y-%m-%d %H:%M")}  |  {self.comment[:64]}...'
