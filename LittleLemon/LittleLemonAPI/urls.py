from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    path('groups/managers/users', views.managers),
    path('groups/managers/users/<int:user_id>', views.delete_manager),
    
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:user_id>', views.delete_delivery_crew),
    
    path('menu-items', views.menu_items),
    path('menu-items/<int:item_id>', views.single_menu_item),
    
    path('cart/menu-items', views.cart_items),
    
    path('orders', views.orders),
    path('orders/<int:order_id>', views.single_order),
]
