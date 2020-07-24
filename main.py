import json
import csv

sensorsMap = {}
payloads_metadata = {}

with open('log.txt', 'r') as myfile:
    data = myfile.read()
    
    payloads = data.split("\n\n\n")
    print("Payload len: " , len(payloads))

    # Get sensor sampling rate
    samplingRates = payloads[-1].split("\n")

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
    counter = 0
    for i in range(1, len(payloads) - 1):
        payload = payloads[i]
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


                    sensor_metadata["timestamp"] = float(sensorsMap[sensor_name]['start_time']) + (1/sensorsMap[sensor_name]['hz']) * counter
                    sensor_metadata["sensor_name"] = sensor_name
                    sensor_metadata["x_value"] = x_value
                    sensor_metadata["y_value"] = y_value
                    sensor_metadata["z_value"] = z_value
                    counter += 1
                    timestamps_metadata.append(sensor_metadata)
                elif len(sentence.split(" ")) == 3:
                    # SHUT sensors sample
                    words = sentence.split(" ")
                    sensor_name = words[0]
                    x_value = words[1]
                    x_value = float(x_value[:x_value.find(",")])
                    sensor_metadata["timestamp"] = float(sensorsMap[sensor_name]['start_time']) + (1/sensorsMap[sensor_name]['hz']) * counter
                    sensor_metadata["sensor_name"] = sensor_name
                    sensor_metadata["x_value"] = x_value
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



    

