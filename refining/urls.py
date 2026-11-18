from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'refining'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # НПЗ
    path('refineries/', views.RefineryListView.as_view(), name='refinery_list'),
    path('refineries/<int:pk>/', views.RefineryDetailView.as_view(), name='refinery_detail'),
    path('refineries/new/', views.refinery_create, name='refinery_create'),
    path('refineries/<int:pk>/edit/', views.refinery_update, name='refinery_update'),

    # Марки нефти
    path('crude/', views.CrudeOilListView.as_view(), name='crudeoil_list'),
    path('crude/<int:pk>/', views.CrudeOilDetailView.as_view(), name='crudeoil_detail'),
    path('crude/new/', views.crudeoil_create, name='crudeoil_create'),
    path('crude/<int:pk>/edit/', views.crudeoil_update, name='crudeoil_update'),

    # Установки
    path('units/', views.UnitListView.as_view(), name='unit_list'),
    path('units/new/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_update, name='unit_update'),

    # Продукты
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/new/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),

    # Партии переработки
    path('batches/', views.BatchListView.as_view(), name='batch_list'),
    path('batches/<int:pk>/', views.BatchDetailView.as_view(), name='batch_detail'),
    path('batches/new/', views.batch_create, name='batch_create'),
    path('batches/<int:pk>/edit/', views.batch_update, name='batch_update'),
    path('batches/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
]
