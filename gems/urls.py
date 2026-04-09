from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('art-board/', views.artBoardView, name='art_board'),
    path('artist/<int:pk>/', views.artistProfileView, name='artist_profile'),
    path('open-calls/', views.openCallsView, name='open_calls'),
    path('open-calls/<int:pk>/apply/', views.applyOpenCallView, name='apply_open_call'),
    path('how-it-works/', views.howItWorksView, name='how_it_works'),
    path('spotlight/', views.artistSpotlightView, name='artist_spotlight'),
    path('events/', views.localEventsView, name='local_events'),
    path('success-stories/', views.successStoriesView, name='success_stories'),
    path('help/', views.helpCenterView, name='help_center'),
    path('privacy/', views.privacyView, name='privacy'),
    path('terms/', views.termsView, name='terms'),

    # Owner
    path('owner/', views.ownerDashboardView, name='owner_dashboard'),
    path('owner/new-call/', views.createOpenCallView, name='create_open_call'),
    path('owner/call/<int:pk>/applications/', views.viewApplicationsView, name='view_applications'),

    # User
    path('user/', views.userDashboardView, name='user_dashboard'),
    path('user/edit-profile/', views.editGemProfileView, name='edit_gem_profile'),
]
