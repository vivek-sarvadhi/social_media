from django.db import models
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver
# from django.urls import reverse
from users.utils import get_random_code
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.shortcuts import reverse
# from django.shortcuts import reverse

# Create your models here.
class ProfileManager(models.Manager):

    def get_all_profile_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        print(qs)

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        print(accepted)

        available = [profile for profile in profiles if profile not in accepted]
        print(available)
        return available


    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles



class Profile(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio ---", max_length=100)
    email = models.EmailField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    profile = models.ImageField(upload_to='profile/', default="../static/image/avatar.png", blank=True)
    friends = models.ManyToManyField(User, blank=True, related_name="friends")
    slug = models.SlugField(unique=True, blank=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = ProfileManager()


    def __str__(self):
        return f"{self.user.username}-{self.created_at.strftime('%d-%m-%y')}"


    def get_absolute_url(self):
        return reverse("detail_profiles_view", kwargs={"slug": self.slug})


    def get_friends(self):
        return self.friends.all()

    def get_friends_no(self):
        return self.friends.all().count()

    def get_post_no(self):
        return self.posts.all().count()

    def get_all_authors_posts(self):
        return self.posts.all()

    def get_likes_given_no(self):
        likes = self.like_set.all()
        print(likes)
        total_liked = 0
        for item in likes:
            if item.value == 'like':
                total_liked += 1
        return total_liked

    def get_likes_recieved_no(self):
        posts = self.posts.all()
        print(posts)
        total_liked = 0
        for item in posts:
            total_liked += item.liked.all().count()
            print(total_liked)
        return total_liked


    __initial_first_name = None
    __initial_last_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_first_name = self.first_name
        self.__initial_last_name = self.last_name

    def save(self, *args, **kwargs):
        ex = False
        to_slug = self.slug
        if self.first_name != self.__initial_first_name or self.last_name != self.__initial_last_name or self.slug=="":
            if self.first_name and self.last_name:
                to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
                ex = Profile.objects.filter(slug=to_slug).exists()
                while ex:
                    to_slug = slugify(to_slug + " " + str(get_random_code()))
                    ex = Profile.objects.filter(slug=to_slug).exists()
            else:
                to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)


STATUS_CHOICE = (
    ('send','send'),
    ('accepted','accepted')
)

class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=10, choices=STATUS_CHOICE)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"

