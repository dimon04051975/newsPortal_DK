from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=0)

    def __repr__(self):
        return f"Author (user.name='{self.user}', rating='{self.rating}')"

    def __str__(self):
        return f"{self.user}"

    def update_rating(self):

        posts_rating = self.posts.aggregate(result=Sum('rating')).get('result')
        comments_rating = self.user.comments.aggregate(result=Sum('rating')).get('result')
        print(f"===== {self.user}: обновляем рейтинг автора =====")
        print(f"Рейтинг постов = {posts_rating}")
        print(f"Рейтинг комментов = {comments_rating}")
        self.rating = 3 * posts_rating + comments_rating
        self.save()
        print(f"Рейтинг = 3 * {posts_rating} + {comments_rating} = {self.rating}")


class Category(models.Model):

    name = models.CharField(unique=True, max_length=128)

    def __repr__(self):
        return f"Category (name='{self.name}')"

    def __str__(self):
        return f"{self.name}"


class Post(models.Model):

    NEWS = 'NW'
    ARTICLE = 'AR'
    CATEGORY_CHOISES = (
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    )

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    date_time = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=2, choices=CATEGORY_CHOISES, default=ARTICLE)
    category = models.ManyToManyField(Category, through="PostCategory")
    title = models.CharField(max_length=128)
    text = models.TextField()
    rating = models.SmallIntegerField(default=0)

    def __repr__(self):
        return f"Post (author.user.name='{self.author.user}', title='{self.title}', rating='{self.rating}'," \
               f"post_type='{self.post_type}')"

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self, length=124) -> str:
        return f"{self.text[:length]}..." if len(self.text) > length else self.text

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()