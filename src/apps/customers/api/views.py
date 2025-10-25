from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from src.apps.core.models import Customers
from .serializers import CustomerSerializer

class CustomerListCreateAPIView(APIView):
    def get(self, request):
        qs = Customers.objects.all().order_by("-id")
        return Response(CustomerSerializer(qs, many=True).data)

    def post(self, request):
        ser = CustomerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

class CustomerDetailAPIView(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        return Response(CustomerSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        ser = CustomerSerializer(obj, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def patch(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        ser = CustomerSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    def delete(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
