import xml.etree.ElementTree as ET 

tree = ET.parse('py_xml/witsml.xml')
root = tree.getroot()

logs_list = []

name = root.find("name").text
long = root.find("location/lon").text
lat = root.find("location/lat").text

print(f"Well: {name} at ({lat}, {long})\n")

for log in root.findall("logs/log"):
    type = log.find("type").text
    unit = log.find("unit").text
    values = []
    
    for value in log.findall("values/value"):
        num = float(value.text)
        values.append(num)
        
    log_dict = {
        "type": type,
        "unit": unit,
        "values": values 
    }
    logs_list.append(log_dict)

for log in logs_list:
    avg = round(sum(log["values"]) / len(log["values"]), 2)
    print(f"{log['type']} ({log['unit']}): {log['values']}")
    print(f"Average {log['type']}: {avg}\n")
