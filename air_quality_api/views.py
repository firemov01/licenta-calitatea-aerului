from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import GraphData, DevelcoDeviceData
from .serializers import GraphDataSerializer, DeviceDataSerializer
from .data_script.data_script import DataScript


class DeviceDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        device_data = DevelcoDeviceData.objects.all()
        serializer = DeviceDataSerializer(device_data, many=True)
        return Response(serializer.data)


class GraphDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        graph_data = GraphData.objects.all()
        serializer = GraphDataSerializer(graph_data, many=True)
        return Response(serializer.data)

    # def post(self, request):
    #     serializer = GraphDataSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScriptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data_script = DataScript()
        if data_script.is_running:
            data_script.stop()
            return Response({'status': 'stopped'})
        else:
            data_script.start()
            return Response({'status': 'started'})

    def get(self, request):
        data_script = DataScript()
        if data_script.is_running:
            return Response({'status': 'running'})
        else:
            return Response({'status': 'stopped'})
