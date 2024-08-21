from copy import deepcopy
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from air_quality_api.services import AutomationService, PredictionService, TipsService
from .models import (
    AutomatedDevice,
    DevelcoDevice,
    DevelcoDeviceData,
    DeviceImage,
    Limits,
    IsAutomaticModeActive,
)
from .serializers import (
    AutomatedDeviceSerializer,
    DevelcoDeviceSerializer,
    DevelcoDeviceStatusSerializer,
    DeviceDataSerializer,
    DeviceImageSerializer,
    LimitsSerializer,
)
from rest_framework.pagination import PageNumberPagination


class DeviceDataView(APIView):
    def get(self, request):
        key = request.query_params.get("key")
        period_type = request.query_params.get("period-type")  # can be day/month/year
        day = request.query_params.get("day")
        month = request.query_params.get("month")
        year = request.query_params.get("year")
        device_name = None
        page_size = request.query_params.get("page-size")
        number_of_elements = request.query_params.get("number-of-elements")

        if key == "temperature":
            device_name = "Air Quality Sensor"
        elif key == "voc":
            # TODO: Change the device name to the correct one
            device_name = "Air Quality Sensor"
            # device_name = "Humidity Sensor"
        elif key == "alarm":
            # TODO: Change the device name to the correct one
            device_name = "Window Sensor"
            # device_name = "Air Quality Sensor"
        elif key == "humidity":
            device_name = "Humidity Sensor"

        if period_type is not None and key != "alarm":
            if period_type == "day":
                # get all the data for the day and make an average by hour
                device_data = DevelcoDeviceData.objects.filter(
                    key=key,
                    develco_device__name=device_name,
                    last_updated__day=day,
                    last_updated__month=month,
                    last_updated__year=year,
                )
                # map through the data and get the hours and remove duplicates
                disponible_hours = list(
                    set([data.last_updated.hour for data in device_data])
                )
                # map through the hours and get the data for each hour
                response = []
                # get the average of the data for each hour
                for hour in disponible_hours:
                    data = device_data.filter(last_updated__hour=hour)
                    # remove any data that is not a number
                    data = [d for d in data if d.value.replace(".", "", 1).isdigit()]
                    average = sum([float(data.value) for data in data]) / len(data)
                    # make a DevelcoDeviceData object with the average and the date
                    new_date = datetime(
                        year=int(year), month=int(month), day=int(day), hour=hour
                    ).isoformat()
                    response.append(
                        DevelcoDeviceData(
                            key=key,
                            value=average,
                            last_updated=new_date,
                            name=data[0].name,
                            type=data[0].type,
                            unit=data[0].unit,
                            access=data[0].access,
                        )
                    )
                return Response(DeviceDataSerializer(response, many=True).data)
            if period_type == "month":
                # get all the data for the month and make an average by day
                device_data = DevelcoDeviceData.objects.filter(
                    key=key,
                    develco_device__name=device_name,
                    last_updated__month=month,
                    last_updated__year=year,
                )
                print(device_data.count())
                # map through the data and get the days and remove duplicates
                disponible_days = list(
                    set([data.last_updated.day for data in device_data])
                )
                # map through the days and get the data for each day
                response = []
                # get the average of the data for each day
                for day in disponible_days:
                    data = device_data.filter(last_updated__day=day)
                    # remove any data that is not a number
                    data = [d for d in data if d.value.replace(".", "", 1).isdigit()]
                    average = sum([float(data.value) for data in data]) / len(data)
                    new_date = datetime(
                        year=int(year), month=int(month), day=day
                    ).isoformat()
                    response.append(
                        DevelcoDeviceData(
                            key=key,
                            value=average,
                            last_updated=new_date,
                            name=data[0].name,
                            type=data[0].type,
                            unit=data[0].unit,
                            access=data[0].access,
                        )
                    )
                return Response(DeviceDataSerializer(response, many=True).data)
            if period_type == "year":
                # get all the data for the year and make an average by month
                device_data = DevelcoDeviceData.objects.filter(
                    key=key, develco_device__name=device_name, last_updated__year=year
                )
                # map through the data and get the months and remove duplicates
                disponible_months = list(
                    set([data.last_updated.month for data in device_data])
                )
                # map through the months and get the data for each month
                response = []
                # get the average of the data for each month
                for month in disponible_months:
                    data = device_data.filter(last_updated__month=month)
                    # remove any data that is not a number
                    data = [d for d in data if d.value.replace(".", "", 1).isdigit()]
                    average = sum([float(data.value) for data in data]) / len(data)
                    new_date = datetime(year=int(year), month=month, day=1).isoformat()
                    response.append(
                        DevelcoDeviceData(
                            key=key,
                            value=average,
                            last_updated=new_date,
                            name=data[0].name,
                            type=data[0].type,
                            unit=data[0].unit,
                            access=data[0].access,
                        )
                    )
                return Response(DeviceDataSerializer(response, many=True).data)
        elif period_type is not None and key == "alarm":
            # get all the data for the day
            device_data = []
            if period_type == "day":
                device_data = DevelcoDeviceData.objects.filter(
                    key=key,
                    develco_device__name=device_name,
                    last_updated__day=day,
                    last_updated__month=month,
                    last_updated__year=year,
                )
            elif period_type == "month":
                device_data = DevelcoDeviceData.objects.filter(
                    key=key,
                    develco_device__name=device_name,
                    last_updated__month=month,
                    last_updated__year=year,
                )
            elif period_type == "year":
                device_data = DevelcoDeviceData.objects.filter(
                    key=key, develco_device__name=device_name, last_updated__year=year
                )

            # map through the data and get the percentage of alarms that are true and false
            response = []
            # get the percentage of alarms that are true and false
            true_alarms = len(device_data.filter(value="True"))
            false_alarms = len(device_data.filter(value="False"))
            percent = 50
            if true_alarms + false_alarms != 0:
                percent = (true_alarms / (true_alarms + false_alarms)) * 100
            if len(device_data) == 0:
                device_data = [DevelcoDeviceData()]
            response.append(
                DevelcoDeviceData(
                    key=key,
                    value=percent,
                    last_updated=datetime(
                        year=int(year), month=int(month), day=int(day)
                    ).isoformat(),
                    name="true_alarms",
                    type=device_data[0].type,
                    unit=device_data[0].unit,
                    access=device_data[0].access,
                )
            )
            response.append(
                DevelcoDeviceData(
                    key=key,
                    value=100 - percent,
                    last_updated=datetime(
                        year=int(year), month=int(month), day=int(day)
                    ).isoformat(),
                    name="false_alarms",
                    type=device_data[0].type,
                    unit=device_data[0].unit,
                    access=device_data[0].access,
                )
            )
            return Response(DeviceDataSerializer(response, many=True).data)

        paginator = PageNumberPagination()
        if page_size is not None:
            paginator.page_size = page_size
        else:
            paginator.page_size = 100

        device_data = DevelcoDeviceData.objects.all()

        if number_of_elements is not None and len(device_data) > int(
            number_of_elements
        ):
            step = len(device_data) // int(number_of_elements)
            device_data = device_data[::step]

        result_page = paginator.paginate_queryset(device_data, request)
        serializer = DeviceDataSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DevelcoDeviceView(APIView):
    def get(self, request, id=None, format=None):
        paginator = PageNumberPagination()
        paginator.page_size = 100

        if id is None:
            develco_device = DevelcoDevice.objects.all()
            result_page = paginator.paginate_queryset(develco_device, request)
            serializer = DevelcoDeviceSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        develco_device = get_object_or_404(DevelcoDevice, device_id=id)
        result_page = paginator.paginate_queryset(develco_device, request)
        serializer = DevelcoDeviceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DevelcoDeviceStatusView(APIView):
    # get the last device data for each device
    def get(self, request):
        develco_devices = DevelcoDevice.objects.all()
        response = []
        for device in develco_devices:
            # get the device_data sorted by date
            device_data = DevelcoDeviceData.objects.filter(
                develco_device=device
            ).order_by("last_updated")
            if len(device_data) > 0:
                # get all the disponible keys
                keys = list(set([data.key for data in device_data]))
                # get the last data for each key
                last_data = []
                for key in keys:
                    data = device_data.filter(key=key).last()
                    last_data.append(data)
                device_with_data = DevelcoDevice()
                # copy the device data to the device_with_data object
                device_with_data.name = device.name
                device_with_data.data = last_data
                response.append(device_with_data)
        serializer = DevelcoDeviceStatusSerializer(response, many=True)
        return Response(serializer.data)


class TipsView(APIView):
    def get(self, request):
        tips = TipsService.get_tips()
        return Response({"tips": tips})


class AutomatedDeviceView(APIView):
    def get(self, request):
        automated_device = AutomatedDevice.objects.all().order_by("id")
        serializer = AutomatedDeviceSerializer(automated_device, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AutomatedDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            AutomationService.automate_devices()
            return Response(serializer.data)
        AutomationService.automate_devices()
        return Response(serializer.errors)

    def patch(self, request, id):
        automated_device = AutomatedDevice.objects.get(id=id)
        serializer = AutomatedDeviceSerializer(
            instance=automated_device, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            AutomationService.automate_devices()
            return Response(serializer.data)
        AutomationService.automate_devices()
        return Response(serializer.errors)

    def delete(self, request, id):
        automated_device = AutomatedDevice.objects.get(id=id)
        automated_device.delete()
        return Response("Item deleted successfully")


class DeviceImageView(APIView):
    def get(self, request):
        device_images = DeviceImage.objects.all()
        serializer = DeviceImageSerializer(device_images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeviceImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def patch(self, request, id):
        device_image = DeviceImage.objects.get(id=id)
        serializer = DeviceImageSerializer(
            instance=device_image, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, id):
        device_image = DeviceImage.objects.get(id=id)
        device_image.delete()
        return Response("Item deleted successfully")


class DevelcoDeviceLimitView(APIView):
    def get(self, request):
        limits = Limits.objects.all().order_by("id")
        serializer = LimitsSerializer(limits, many=True)
        return Response(serializer.data)

    def patch(self, request, id):
        limits = Limits.objects.get(id=id)
        serializer = LimitsSerializer(instance=limits, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            AutomationService.automate_devices()
            return Response(serializer.data)
        AutomationService.automate_devices()
        return Response(serializer.errors)


class DeviceDataPredictionView(APIView):

    def get(self, request):
        prediction_service = PredictionService()

        key = request.query_params.get("key")
        period_type = request.query_params.get("period-type")  # can be day/month/year
        day = request.query_params.get("day")
        month = request.query_params.get("month")
        year = request.query_params.get("year")

        if period_type is not None and key != "alarm":
            if period_type == "day":
                response = []
                disponible_hours = list(range(0, 24))
                # for each hour add the year, month, day and hour to the response
                disponible_hours = [
                    datetime(year=int(year), month=int(month), day=int(day), hour=hour)
                    for hour in disponible_hours
                ]
                # get the average of the data for each hour
                predictions = prediction_service.get_predictions(disponible_hours)
                # add the predictions to the response
                if key == "temperature":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[3],
                            last_updated=datetime(
                                year=int(year),
                                month=int(month),
                                day=int(day),
                                hour=index,
                            ).isoformat(),
                            name="Temperature",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "voc":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[4],
                            last_updated=datetime(
                                year=int(year),
                                month=int(month),
                                day=int(day),
                                hour=index,
                            ).isoformat(),
                            name="VOC",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "humidity":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[0],
                            last_updated=datetime(
                                year=int(year),
                                month=int(month),
                                day=int(day),
                                hour=index,
                            ).isoformat(),
                            name="Humidity",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                return Response(DeviceDataSerializer(response, many=True).data)
            if period_type == "month":
                response = []
                # get how many days are in the month
                from calendar import monthrange

                # Assuming 'year' and 'month' are your year and month
                _, days_in_month = monthrange(int(year), int(month))
                disponible_days = list(range(1, days_in_month + 1))
                # for each day add the year, month and day to the response
                disponible_days = [
                    datetime(year=int(year), month=int(month), day=day, hour=12)
                    for day in disponible_days
                ]
                # get the average of the data for each day
                predictions = prediction_service.get_predictions(disponible_days)
                # add the predictions to the response
                if key == "temperature":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[3],
                            last_updated=datetime(
                                year=int(year), month=int(month), day=index + 1
                            ).isoformat(),
                            name="Temperature",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "voc":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[4],
                            last_updated=datetime(
                                year=int(year), month=int(month), day=index + 1
                            ).isoformat(),
                            name="VOC",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "humidity":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[0],
                            last_updated=datetime(
                                year=int(year), month=int(month), day=index + 1
                            ).isoformat(),
                            name="Humidity",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                return Response(DeviceDataSerializer(response, many=True).data)
            if period_type == "year":
                # get all the data for the year and make an average by month
                response = []
                # get the average of the data for each month
                predictions = prediction_service.get_predictions(
                    [
                        datetime(year=int(year), month=month, day=1, hour=12)
                        for month in range(1, 13)
                    ]
                )
                # add the predictions to the response
                if key == "temperature":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[3],
                            last_updated=datetime(
                                year=int(year), month=index + 1, day=1
                            ).isoformat(),
                            name="Temperature",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "voc":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[4],
                            last_updated=datetime(
                                year=int(year), month=index + 1, day=1
                            ).isoformat(),
                            name="VOC",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                elif key == "humidity":
                    response = [
                        DevelcoDeviceData(
                            key=key,
                            value=prediction[0],
                            last_updated=datetime(
                                year=int(year), month=index + 1, day=1
                            ).isoformat(),
                            name="Humidity",
                        )
                        for index, prediction in enumerate(predictions)
                    ]
                return Response(DeviceDataSerializer(response, many=True).data)

        return Response({"error": "Invalid query parameters"})


class ModeView(APIView):

    def get(self, request):
        mode = IsAutomaticModeActive.objects.first()
        return Response({"is_active": mode.is_active})

    def patch(self, request):
        mode = IsAutomaticModeActive.objects.first()
        mode.is_active = not mode.is_active
        mode.save()
        AutomationService.automate_devices()
        return Response({"is_active": mode.is_active})
