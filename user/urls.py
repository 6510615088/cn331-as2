from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('register/<int:subject_id>/', views.register_subject, name='register_subject'),
    path('unregister/<int:subject_id>/', views.unregister_subject, name='unregister_subject'),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
