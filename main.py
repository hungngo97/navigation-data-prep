import json
import csv
from collections import defaultdict


sensorsMap = {}
payloads_metadata = {}
raw_payloads = []

with open('log.txt', 'r') as myfile:
    data = myfile.read()
    
    raw_payloads = data.split("\n\n\n")
    print("Payload len: " , len(raw_payloads))

    # Get sensor sampling rate
    samplingRates = raw_payloads[-1].split("\n")

    for samplingRate in samplingRates:
        words = samplingRate.split(" ")
        sensor = words[0]
        if sensor:
            hz = words[4]
            hz = float(hz[:hz.find("Hz")])

            start_time = words[6]
            
            end_time = words[8]
            end_time = end_time[:end_time.find(")")]

            sensorsMap[sensor] = {
                "hz": hz,
                "start_time": start_time,
                "end_time": end_time
            }
            print(sensor, sensorsMap[sensor])
    
    # Get time of each sensor sample
    sensor_counter = defaultdict(int)
    for i in range(1, len(raw_payloads) - 1):
        payload = raw_payloads[i]
        sensors_payload = payload.split("\n\n")
        
        payloads_metadata[i] = {}
        for sensor_payload in sensors_payload:
            timestamps_metadata = []
            for sentence in sensor_payload.split("\n"):
                sensor_metadata = {}
                if len(sentence.split(" ")) == 7:
                    # First line that describe start time
                    sensor_metadata["start_time"] = sentence.split(" ")[3]
                    sensor_metadata["end_time"] = sentence.split(" ")[4]
                elif len(sentence.split(" ")) == 5:
                    # ACCL & GYRO
                    words = sentence.split(" ")
                    sensor_name = words[0]
                    x_value = words[1]
                    y_value = words[2]
                    z_value = words[3]

                    x_value = float(x_value[:x_value.find(",")])
                    y_value = float(y_value[:y_value.find(",")])
                    z_value = float(z_value[:z_value.find(",")])


                    sensor_metadata["timestamp"] = float(sensorsMap[sensor_name]['start_time']) + (1/sensorsMap[sensor_name]['hz']) * sensor_counter[sensor_name]
                    sensor_metadata["sensor_name"] = sensor_name
                    sensor_metadata["x_value"] = x_value
                    sensor_metadata["y_value"] = y_value
                    sensor_metadata["z_value"] = z_value
                    sensor_counter[sensor_name] += 1
                    timestamps_metadata.append(sensor_metadata)
                elif len(sentence.split(" ")) == 3:
                    # SHUT sensors sample
                    words = sentence.split(" ")
                    sensor_name = words[0]
                    x_value = words[1]
                    x_value = float(x_value[:x_value.find(",")])
                    sensor_metadata["timestamp"] = float(sensorsMap[sensor_name]['start_time']) + (1/sensorsMap[sensor_name]['hz']) * sensor_counter[sensor_name]
                    sensor_metadata["sensor_name"] = sensor_name
                    sensor_metadata["x_value"] = x_value
                    sensor_counter[sensor_name] += 1
                    timestamps_metadata.append(sensor_metadata)

            if len(timestamps_metadata) > 1:
                sensor_name = timestamps_metadata[1]['sensor_name']
                payloads_metadata[i][sensor_name] = timestamps_metadata

with open('sensorsMap.csv', 'wb') as csv_file:  # Just use 'w' mode in 3.x
    writer = csv.writer(csv_file)
    for key, value in sensorsMap.items():
        row = [key]
        for field, data in value.items():
            row.append(data)
        writer.writerow(row)

with open('payload_metadata.json', 'w+') as f:
    # this would place the entire output on one line
    # use json.dump(lista_items, f, indent=4) to "pretty-print" with four spaces per indent
    json.dump(payloads_metadata, f, indent=4)



min_frequency = min(
    sensorsMap['ACCL']['hz'],
    sensorsMap['GYRO']['hz'],
)

with open('imu.csv', 'w') as imu_csv:
    imu_writer = csv.writer(imu_csv, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(1, len(raw_payloads) - 1):
        sensors_map = payloads_metadata[i]
        accl_samples = sensors_map['ACCL']
        gyro_samples = sensors_map['GYRO']
        row_values = []

        # TODO: Currently the GYRO frequency is 2x ACCL frequency, so index 1 of ACCL is GYRO of index 2
        for accl_index in range(len(accl_samples)):
            gyro_index = accl_index * 2
            accl_value = accl_samples[accl_index]
            gyro_value = gyro_samples[gyro_index]

            row_values = [
                min(accl_value['timestamp'], gyro_value['timestamp']),
                gyro_value['x_value'], gyro_value['y_value'], gyro_value['z_value'],
                accl_value['x_value'], accl_value['y_value'], accl_value['z_value']
            ]
            imu_writer.writerow(row_values)

with open('shut_frame.csv', 'w') as shut_csv:
    shut_writer = csv.writer(shut_csv, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in range(1, len(raw_payloads) - 1):
        sensors_map = payloads_metadata[i]
        shut_samples = sensors_map['SHUT']
        row_values = []

        # TODO: Currently the GYRO frequency is 2x ACCL frequency, so index 1 of ACCL is GYRO of index 2
        for shut_index in range(len(shut_samples)):
            shut_value = shut_samples[shut_index]
            row_values = [
                shut_value['timestamp'],
                shut_value['x_value']
            ]
            shut_writer.writerow(row_values)



            
        

