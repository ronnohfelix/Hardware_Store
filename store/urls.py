from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),

    path('signin/', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),

    path('store/', views.store, name='store'),
    path('logout/', views.logout_view, name='logout'),

    path('search/', views.search_view, name='search'),
]