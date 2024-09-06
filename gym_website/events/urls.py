from django.urls import path
from . import views

urlpatterns = [
    # URL pattern for viewing events of a specific gym
    path('events/', views.view_all_events, name='view_all_events'),
    path('events/<uuid:gym_id>/', views.view_events_by_gym, name='view_events_by_gym'),
    path('events/<uuid:event_id>/', views.delete_event, name='delete_event'),

    # URL pattern for adding a new event
    path('add-event/', views.add_event, name='add_event'),

    # URL pattern for updating an existing event
    path('update-event/', views.update_event, name='update_event'),

]
