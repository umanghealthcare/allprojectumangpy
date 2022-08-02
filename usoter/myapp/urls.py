from django.urls import path,include
from .import views
urlpatterns = [
    path('',views.index,name='index'),
    path('header/',views.header,name='header'),
    path('shop/',views.shop,name='shop'),
    path('single_product/',views.single_product,name='single_product'),
    path('checkout/',views.checkout,name='checkout'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('profile/',views.profile,name='profile'),
    path('change_password/',views.change_password,name='change_password'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('change/',views.change,name='change'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_product_details/<int:pk>/',views.seller_product_details,name='seller_product_details'),    
    path('seller_edit_product/<int:pk>/',views.seller_edit_product,name='seller_edit_product'),
    path('seller_delete_product/<int:pk>/',views.seller_delete_product,name='seller_delete_product'),
    path('single_product/<int:pk>/',views.single_product,name='single_product'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),    
    path('remove_form_wishlist/<int:pk>/',views.remove_form_wishlist,name='remove_form_wishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.cart,name='cart'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('change_qty/<int:pk>/',views.change_qty,name='change_qty'),
    path('pay/', views.initiate_payment, name='pay'),
    path('callback/',views.callback, name='callback'),
    path('myorder/',views.myorder,name='myorder'),
]       