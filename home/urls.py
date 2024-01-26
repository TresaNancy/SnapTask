from django.urls import path
from .import views

urlpatterns = [
    path('',views.home, name='home'), 
    path('signup/',views.signup, name='signup'),
    path('snaptask/',views.snaptask, name='snaptask'), 
    path('user_signin/',views.user_signin, name='user_signin'),
    path('add_task/', views.add_task, name='add_task'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
     path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
      path('update_task_status/', views.update_task_status, name='update_task_status'),
      path('delete_all_tasks/', views.delete_all_tasks, name='delete_all_tasks'),
       path('complete_all_tasks/', views.complete_all_tasks, name='complete_all_tasks'),
    # path('display_task/', views.display_task, name='display_task'),
    # Add your URL pattern
    # Add more URL patterns as needed
]
