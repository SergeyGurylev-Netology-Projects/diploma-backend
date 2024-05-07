from django.urls import path, include

from .views import UserView, FileView, UserSettingsView

urlpatterns = [
    path('user', UserView.as_view({
        'get': 'user_list',
        'post': 'user_create',
    })),
    path('user/<pk>', UserView.as_view({
        'get': 'user_list',
        'patch': 'user_update',
        'delete': 'user_destroy'
    })),
    path('file', FileView.as_view({
        'get': 'file_list',
        'post': 'file_create'
    })),
    path('file/<pk>', FileView.as_view({
        'get': 'file_list',
        'patch': 'file_update',
        'delete': 'file_destroy'
    })),
    path('settings', UserSettingsView.as_view({
        'get': 'settings_list',
        'patch': 'settings_update',
    })),
]
