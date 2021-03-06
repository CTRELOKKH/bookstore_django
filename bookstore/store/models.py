from time import time

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


def gen_slug(s):
    new_slug = slugify(s, allow_unicode=True)
    return new_slug + '-' + str(int(time()))


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, blank=True, unique=True)

    def __str__(self):
        return '{}'.format(self.first_name + ' ' + self.last_name)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.first_name + self.last_name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['last_name']


class Genre(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, blank=True, unique=True)

    def __str__(self):
        return '{}'.format(self.title)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['title']


def cover_upload_path(instanse, filename):
    return "/".join(['books', str(instanse.id), filename])


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    description = models.TextField(default="")
    publish_date = models.DateField(default=timezone.now())
    price = models.DecimalField(decimal_places=2, max_digits=8)
    stock = models.IntegerField(default=0)
    cover_image = models.ImageField(upload_to=cover_upload_path, default='books/empty_cover.jpg')

    genres = models.ManyToManyField('Genre', blank=True, related_name='books')
    authors = models.ManyToManyField('Author', blank=True, related_name='books')

    def get_genres(self):
        return "\n".join([g.title for g in self.genres.all()])

    def get_authors(self):
        return "\n".join([g.first_name + ' ' + g.last_name for g in self.authors.all()])

    def get_reviews(self):
        reviews = Review.objects.filter(book=self)
        print(reviews)
        return list(reviews)


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default="")
    publish_date = models.DateField(default=timezone.now())
    latitude = models.TextField(default="50.45466")
    longitude = models.TextField(default="30.5238")

    def book_title(self):
        print(self.book.title)
        return "\n".join([self.book.title])

    def __str__(self):
        return self.text


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    order_date = models.DateField(null=True)
    payment_type = models.CharField(max_length=100, null=True)
    payment_id = models.CharField(max_length=100, null=True)

    def add_to_cart(self, book_id):
        book = Book.objects.get(pk=book_id)
        try:
            preexisting_order = BookOrder.objects.get(book=book, cart=self)
            preexisting_order.quantity += 1
            preexisting_order.save()
        except BookOrder.DoesNotExist:
            new_order = BookOrder.objects.create(
                book=book,
                cart=self,
                quantity=1,
            )
            new_order.save()

    def remove_from_cart(self, book_id):
        book = Book.objects.get(pk=book_id)
        try:
            preexisting_order = BookOrder.objects.get(book=book, cart=self)
            if preexisting_order.quantity > 1:
                preexisting_order.quantity -= 1
                preexisting_order.save()
            else:
                preexisting_order.delete()
        except BookOrder.DoesNotExist:
            pass


class BookOrder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
