from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from django.contrib.auth.models import User, Group

from .models import *
from .serializers import *
from .permissions import *


# Create your views here.
def index(request):
    return Response({"hello": "world"})


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def managers(request):
    managers = Group.objects.get(name="Managers")

    if request.method == "GET":
        allManagers = managers.user_set.all()
        return Response({"Managers": list(allManagers.values("id", "username"))})
    elif request.method == "POST":
        username = request.data["username"]
        if not username:
            return Response(
                {"message": "username is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, username=username)
        if user in managers.user_set.all():
            return Response(
                {"message": f"{username} is already a manager"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        managers.user_set.add(user)
        return Response(
            {"message": f"{username} added to managers"}, status=status.HTTP_201_CREATED
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_manager(request, user_id):
    managers = Group.objects.get(name="Managers")

    user = get_object_or_404(User, id=user_id)
    if user not in managers.user_set.all():
        return Response(
            {"message": f"{user.username} is not a manager"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    managers.user_set.remove(user)
    return Response(
        {"message": f"{user.username} removed from managers"}, status=status.HTTP_200_OK
    )


@api_view(["GET", "POST"])
@permission_classes([IsAdminUser])
def delivery_crew(request):
    delivery_crew = Group.objects.get(name="Delivery Crew")

    if request.method == "GET":
        allDeliveryCrew = delivery_crew.user_set.all()
        return Response(
            {"Delivery Crew": list(allDeliveryCrew.values("id", "username"))}
        )
    elif request.method == "POST":
        username = request.data["username"]
        if not username:
            return Response(
                {"message": "username is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, username=username)
        if user in delivery_crew.user_set.all():
            return Response(
                {"message": f"{username} is already a delivery crew"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        delivery_crew.user_set.add(user)
        return Response(
            {"message": f"{username} added to delivery crew"},
            status=status.HTTP_201_CREATED,
        )


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_delivery_crew(request, user_id):
    delivery_crew = Group.objects.get(name="Delivery Crew")

    user = get_object_or_404(User, id=user_id)
    if user not in delivery_crew.user_set.all():
        return Response(
            {"message": f"{user.username} is not a delivery crew"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    delivery_crew.user_set.remove(user)
    return Response(
        {"message": f"{user.username} removed from delivery crew"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
def menu_items(request):
    if request.method == "GET":
        data = MenuItem.objects.all()
        items = MenuItemSerializer(data, many=True)
        return Response({"Menu Items": items.data}, status=status.HTTP_200_OK)
    elif request.method == "POST":
        if not is_admin_or_manager(request):
            return Response(
                {"message": "You are not authorized to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MenuItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def single_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    if request.method == "GET":
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        if not is_admin_or_manager(request):
            return Response(
                {"message": "You are not authorized to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        if not is_admin_or_manager(request):
            return Response(
                {"message": "You are not authorized to perform this action"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        item.delete()
        return Response(
            {"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET", "POST", "DELETE"])
def cart_items(request):
    if request.method == "GET":
        user = request.user
        cart = Cart.objects.filter(user=user)
        if not cart:
            return Response(
                {"message": "No items in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = CartSerializer(cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        mutable_data = request.data.copy()
        user = request.user
        mutable_data["user"] = user.id

        serializer = CartSerializer(data=mutable_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        user = request.user
        cart = Cart.objects.filter(user=user)
        if not cart:
            return Response(
                {"message": "No items in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        cart.delete()
        return Response(
            {"message": "Cart Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


@api_view(["GET", "POST"])
def orders(request):
    if request.method == "GET":
        user = request.user
        if is_admin_or_manager(request):
            all_orders = Order.objects.all()
            serializer = OrderSerializer(all_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        if is_delivery_crew(request):
            all_orders = Order.objects.filter(delivery_crew=user)
            serializer = OrderSerializer(all_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        orders = Order.objects.filter(user=user)
        if not orders:
            return Response(
                {"message": "No orders found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        user = request.user
        cart = Cart.objects.filter(user=user)
        if not cart:
            return Response(
                {"message": "No items in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        total = sum([item.price for item in cart])
        order = Order.objects.create(user=user, total=total)

        for item in cart:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

        cart.delete()
        return Response(
            {"message": "Order placed successfully"}, status=status.HTTP_201_CREATED
        )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAdminOrManagerUser])
def single_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "PUT":
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        

def is_admin_or_manager(request):
    return request.user.is_authenticated and (
        request.user.is_superuser
        or request.user.groups.filter(name="Managers").exists()
    )


def is_delivery_crew(request):
    return request.user.is_authenticated and request.user.groups.filter(name="Deliver Crew").exists()
    
