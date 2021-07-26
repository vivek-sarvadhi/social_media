from django.urls import path
from users.views import (my_profile_view, 
                        invites_received_view, 
                        ProfileDetailView,
                        ProfileListView, 
                        invite_profiles_list_view, 
                        send_invatation, 
                        remove_friends,
                        accept_invitation,
                        reject_invitation,
                        delete_image,
                        # my_profile_image_view,
                        )

urlpatterns = [
    path("", ProfileListView.as_view(), name="all_profiles_view"),
    path("myprofile/", my_profile_view, name="myprofile"),
    # path("myprofileimage/", my_profile_image_view, name="myprofileimage"),
    path("myinvites/", invites_received_view, name="my_invites"),
    path("inviteprofile/", invite_profiles_list_view, name="invite_profiles_view"),
    path("sendinvite/", send_invatation, name="send_invite"),
    path("removefriend/", remove_friends, name="remove_friend"),
    path("myinvites/accept", accept_invitation, name="accept_invite"),
    path("myinvites/reject", reject_invitation, name="reject_invite"),
    path("imagedelete/<int:pk>/", delete_image, name="delete_image"),
    path("<slug>/", ProfileDetailView.as_view(), name="detail_profiles_view"),
]