from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from src.apps.core.models import Customers
from .serializers import CustomerSerializer

class CustomerListCreateAPIView(APIView):
    @extend_schema(
        responses=CustomerSerializer(many=True)
    )
    def get(self, request):
        qs = Customers.objects.all().order_by("-id")
        return Response(CustomerSerializer(qs, many=True).data)

    @extend_schema(
        request=CustomerSerializer,
        responses={201: CustomerSerializer}
    )
    def post(self, request):
        ser = CustomerSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)

class CustomerDetailAPIView(APIView):
    @extend_schema(request=CustomerSerializer, responses=CustomerSerializer)
    def get(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        return Response(CustomerSerializer(obj).data)

    @extend_schema(request=CustomerSerializer, responses=CustomerSerializer)
    def put(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        ser = CustomerSerializer(obj, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    @extend_schema(request=CustomerSerializer, responses=CustomerSerializer)
    def patch(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        ser = CustomerSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

    @extend_schema(
        responses={204: OpenApiResponse(description="Soft deleted")}
    )
    def delete(self, request, pk):
        obj = get_object_or_404(Customers, pk=pk)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
