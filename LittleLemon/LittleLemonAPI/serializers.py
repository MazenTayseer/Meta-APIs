from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "groups"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category_name", "category"]

    def create(self, data):
        category_name = data.pop("category_name")
        category = Category.objects.get(title=category_name)
        data["category"] = category
        return MenuItem.objects.create(**data)


class CartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(
        read_only=True, max_digits=6, decimal_places=2
    )
    price = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)

    class Meta:
        model = Cart
        fields = ["user", "menuitem", "quantity", "unit_price", "price"]

    def create(self, data):
        user = data["user"]
        menuitem_id = data["menuitem"].id
        quantity = data["quantity"]

        menu_item = MenuItem.objects.get(id=menuitem_id)
        unit_price = menu_item.price
        price = unit_price * quantity

        cart_item = Cart.objects.create(
            user=user,
            menuitem=menu_item,
            quantity=quantity,
            unit_price=unit_price,
            price=price,
        )

        return cart_item


class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "total", "date"]
        read_only_fields = ["id", "user", "total", "date"]


