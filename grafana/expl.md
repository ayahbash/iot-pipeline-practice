# grafana + influx demo

Grafana dashboard for visualizing drilling sensor data (rop, torque, pressure..) from InfluxDB.

this is a template ready to import; works with any InfluxDB measurement that uses the same fields and tags.

---

## folder structure

```

grafana/
├── dashboard.json   # Grafana dashboard ready to import
├── data.py          # python script to generate values
└── expl.md

````

---

## setup

1. **run InfluxDB** (docker)
```bash.8
docker run -d -p 8086:8086 --name influxdb influxdb:1.8
````

* create a bucket (default: `drilling_data`)
* create an all-access token and note your organization name

2. **run Grafana** (docker)

```bash
docker run -d -p 3000:3000 --name grafana grafana/grafana
```

* import `dashboard.json`
* add your InfluxDB bucket as a data source

---

## dashboard notes
- **8 rows:** well states, operational summary, drilling performance, mechanics, hydraulics, depth, gas & mud, per-well view
- **panels:** one panel per field (rop, rpm, torque, pressure, flow, gas, depth, etc.)
- **lines:** one line per `well_id` (well-01, well-02, well-03)
- **refresh interval:** 2 seconds
- **time range:** last 2 minutes (real-time view)
- **color coding:** per well (teal, red, amber) and per operational state (forage, circulation, connexion)
- **alarm thresholds:** configured on critical parameters: rop, torque, hookload, pressure, flow, total gas

> panels automatically show all 3 wells. dashboard json can be imported directly into any grafana instance connected to influxdb.

---

## optional: python script demo

* `data.py` sends simulated drilling data to InfluxDB for testing
* you can modify it locally to match real data
* not required to use dashboard

---

## using your own data

* send your data to InfluxDB (measurement, fields, tag `well_id`, timestamp `_time`)
* update Grafana panel filters if needed (bucket, measurement, field)
* dashboard will update automatically for all wells
