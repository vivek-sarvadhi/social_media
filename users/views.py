from django import forms
from django.db.models.query import QuerySet
from django.dispatch.dispatcher import receiver
from django.forms import models
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from users.models import Profile, Relationship
from users.forms import ProfileModelForm, ProfileImageModelForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def home_view(request):
    # user = request.user
    hello = "Hello World!"
    context = {
        # 'user':user,
        'hello':hello
    }
    return render(request, 'users/home.html', {'user':'user','hello':hello})


@login_required
def my_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    # form = ProfileModelForm(request.POST or None,request.FILES or None, instance=profile)
    
    confirm = False
    if request.method == 'POST':

        form = ProfileImageModelForm(request.POST or None, request.FILES or None, instance=profile)
        form1 = ProfileModelForm(request.POST or None, instance=profile)
        print("form == > ", form)
        print("form1 == > ", form1)
        print(form1.is_valid)
        if form1.is_valid():
            print("form.....",form.cleaned_data)
            form1.save()
            confirm = True

        elif form.is_valid():
            print("hello",form.cleaned_data)
            form.save()
            confirm = True
    else:
        form1 = ProfileModelForm()
        form = ProfileImageModelForm()

    context = {
        'profile':profile,
        'form':form,
        'form1':form1,
        'confirm':confirm
    }
    return render(request, 'users/myprofile.html', context)


# @login_required
# def my_profile_image_view(request):
#     profile = Profile.objects.get(user=request.user)
#     form = ProfileImageModelForm(request.POST or None, request.FILES or None, instance=profile)
#     confirm = False

#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             confirm = True

#     context = {
#         'profile':profile,
#         'form':form,
#         'confirm':confirm
#     }
#     return render(request, 'users/myprofile.html', context)


@login_required
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True
    context = {
        'qs': results,
        'is_empty': is_empty
    }

    return render(request, 'users/my_invites.html', context)


@login_required
def accept_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect('my_invites')


@login_required
def reject_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('my_invites')


@login_required
def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profile_to_invite(user)
    context = {
        'qs': qs
    }
    return render(request, 'users/to_invite_list.html', context)


# def profiles_list_view(request):
#     user = request.user
#     qs = Profile.objects.get_all_profiles(user)

#     context = {
#         'qs': qs
#     }
#     return render(request, 'users/profile_list.html', context)

class ProfileDetailView(LoginRequiredMixin ,DetailView):
    model = Profile
    template_name = 'users/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['posts'] = self.get_object().get_all_authors_posts()
        context['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False
        return context


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'users/profile_list.html'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context['rel_receiver'] = rel_receiver
        context['rel_sender'] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        return context


@login_required
def send_invatation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('myprofile')


@login_required
def remove_friends(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel  = Relationship.objects.get((Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender)))
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('myprofile')



def delete_image(request, pk):
    image_pk = Profile.objects.get(pk=pk)

    # image = Profile.objects.filter(profile=image_pk.profile)
    # print(image)
    # hello = image_pk.profile
    # print("hello =======>",image)
    # image.delete()
    # image = Profile.objects.filter(profile=image_pk.profile)
    # print("=====>",image)
    # image_pk.profile.delete()
    # return redirect('myprofile')