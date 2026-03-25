import xml.etree.ElementTree as ET 

tree = ET.parse('py_xml/witsml.xml')
root = tree.getroot()

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
        
    
    avg = round(sum(values) / len(values), 2)
    print(f"{type} {unit}: {values}")
    print(f"Average {type}: {avg}\n")
