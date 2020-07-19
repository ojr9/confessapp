from datetime import timedelta, datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

"""
    The point here is to register good and bad actions. Maybe have a tally of how many times each action was committed.
    Also have a catalog of actions. 
     
"""
# Have a catalog object to gather all categories? Opting for not, atm.

usr = get_user_model()


class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['category_name']

    def sluggy(self):
        self.slug = slugify(self.category_name)
        self.save()

    def __str__(self):
        return self.category_name


class Deed(models.Model):
    user = models.ForeignKey(usr, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    situation = models.TextField(blank=True, null=True)
    registered = models.DateTimeField(auto_now_add=True)
    intensity = models.PositiveSmallIntegerField(choices=((1, 'Tiny'), (2, 'Easy'), (3, 'Casual'), (4, 'Hard'), (5, 'Mindblowing')))
    private = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    reflection = models.TextField(blank=True, null=True)
    likes = models.PositiveSmallIntegerField(default=0)
    applauses = models.PositiveSmallIntegerField(default=0)
    mehs = models.PositiveSmallIntegerField(default=0)
    laughs = models.PositiveSmallIntegerField(default=0)
    cries = models.PositiveSmallIntegerField(default=0)
    nature = models.CharField(max_length=4, choices=(('Good', 'Good'), ('Bad', 'Bad')))
    locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-registered']

    def reaction(self, reaction):
        if reaction in ['li', 'ap', 'me', 'la', 'cr']:
            if reaction == 'li':
                self.likes += 1
            elif reaction == 'ap':
                self.applauses += 1
            elif reaction == 'me':
                self.mehs += 1
            elif reaction == 'la':
                self.laughs += 1
            elif reaction == 'cr':
                self.cries += 1
            self.save()
        return

    def __str__(self):
        return str(self.pk)

    def get_absolute_url(self):
        return reverse('view_deed', kwargs={'id': self.pk})


class Collection(models.Model):
    deed = models.OneToOneField(Deed, on_delete=models.CASCADE, related_name='collection')
    price = models.IntegerField(default=1.00)
    update = models.DateTimeField(default=timezone.now)

    def _price_date(self):
        votes = {'likes': self.deed.likes, 'applauses': self.deed.applauses, 'mehs': self.deed.mehs,
                 'laughs': self.deed.laughs, 'cries': self.deed.cries}
        value = round((votes['likes'] + votes['applauses']*2 - votes['mehs']*0.5 - votes['laughs']
                             - votes['cries']*2), 2)
        print(value, self.price)
        self.price = self.price + value
        self.update = timezone.now()
        self.save()

    def price_update(self):
        if timezone.now() > (self.update + timedelta(minutes=30)):
            self._price_date()
            return self
        return None

    def __str__(self):
        return f'{self.pk} Collection for {self.deed}'


class Comment(models.Model):
    deed = models.ForeignKey(Deed, on_delete=models.CASCADE, related_name='comment')
    user = models.ForeignKey(usr, on_delete=models.CASCADE, related_name='comment_writer')
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()

    def __str__(self):
        return f'{self.id} Comment on {self.deed}'
