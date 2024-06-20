import re
import json
import time
from air_quality_api.models import DevelcoDeviceData

camel_pat = re.compile(r"([A-Z])")
under_pat = re.compile(r"_([a-z])")


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: "_" + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert_json(d, convert):
    if isinstance(d, dict):
        new_d = {}
        for k, v in d.items():
            new_d[convert(k)] = convert_json(v, convert)
        return new_d
    elif isinstance(d, list):
        return [convert_json(x, convert) for x in d]
    else:
        return d


def convert_load(*args, **kwargs):
    json_obj = json.load(*args, **kwargs)
    return convert_json(json_obj, camel_to_underscore)


def convert_dump(*args, **kwargs):
    args = (convert_json(args[0], underscore_to_camel),) + args[1:]
    json.dump(*args, **kwargs)


def functiondelay(function):
    def wrapper(*args, **kwargs):
        time.sleep(2)
        return function(*args, **kwargs)

    wrapper.nodelay = function
    return wrapper


# function to save all the data from the db to a csv file
def save_to_csv():
    # create a csv file
    with open("device_data.csv", "w") as file:
        # write the header witch should have the nesxt columns: id, date, h_humidity, h_temperature, a_humidity, a_temperature, a_voc, w_temperature, w_alarm
        file.write(
            "id,date,h_humidity,h_temperature,a_humidity,a_temperature,a_voc,w_temperature,w_alarm\n"
        )

        # get all the data from the db in batches of 1000 using iterator
        number_of_device_data = DevelcoDeviceData.objects.count()

        # a map of field names and their corresponding values
        field_name_map = {
            "id": None,
            "date": None,
            "h_humidity": None,
            "h_temperature": None,
            "a_humidity": None,
            "a_temperature": None,
            "a_voc": None,
            "w_temperature": None,
            "w_alarm": None,
        }

        number_of_elements_saved = 2

        for i in range(0, number_of_device_data, 1000):
            device_data_list = DevelcoDeviceData.objects.all()[i : i + 1000]
            # write the data to the csv
            for device_data in device_data_list:
                field_name_map["id"] = device_data.id
                field_name_map["date"] = device_data.last_updated
                if device_data.develco_device.name == "SquidZigBee":
                    if device_data.key == "humidity":
                        field_name_map["h_humidity"] = device_data.value
                        number_of_elements_saved += 1
                    elif device_data.key == "temperature":
                        field_name_map["h_temperature"] = device_data.value
                        number_of_elements_saved += 1
                elif device_data.develco_device.name == "Humidity Sensor":
                    if device_data.key == "humidity":
                        field_name_map["a_humidity"] = device_data.value
                        number_of_elements_saved += 1
                    elif device_data.key == "temperature":
                        field_name_map["a_temperature"] = device_data.value
                        number_of_elements_saved += 1
                    elif device_data.key == "voc":
                        field_name_map["a_voc"] = device_data.value
                        number_of_elements_saved += 1
                elif device_data.develco_device.name == "Air Quality Sensor":
                    if device_data.key == "temperature":
                        field_name_map["w_temperature"] = device_data.value
                        number_of_elements_saved += 1
                    elif device_data.key == "alarm":
                        field_name_map["w_alarm"] = device_data.value
                        number_of_elements_saved += 1
                if number_of_elements_saved == 9:
                    file.write(
                        f"{field_name_map['id']},{field_name_map['date']},{field_name_map['h_humidity']},{field_name_map['h_temperature']},{field_name_map['a_humidity']},{field_name_map['a_temperature']},{field_name_map['a_voc']},{field_name_map['w_temperature']},{field_name_map['w_alarm']}\n"
                    )
                    number_of_elements_saved = 2
