from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import DevelcoDevice, DevelcoDeviceData
from .serializers import DevelcoDeviceSerializer, DeviceDataSerializer


class DeviceDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        device_data = DevelcoDeviceData.objects.all()
        serializer = DeviceDataSerializer(device_data, many=True)
        return Response(serializer.data)


class DevelcoDeviceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id=None, format=None):
        if id is None:
            develco_device = DevelcoDevice.objects.all()
            serializer = DevelcoDeviceSerializer(develco_device, many=True)
            return Response(serializer.data)

        develco_device = get_object_or_404(DevelcoDevice, device_id=id)
        serializer = DevelcoDeviceSerializer(develco_device, many=False)
        return Response(serializer.data)
