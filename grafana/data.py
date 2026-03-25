import time, random
from influxdb import InfluxDBClient

# influx config
client = InfluxDBClient(host='your_host', port=your_port, database='drilling_data')
client.create_database('drilling_data')

# config
WELLS = ["Well-01", "Well-02", "Well-03"]
STATES = ["DRILLING", "CONNECTION", "CIRCULATING"]
INTERVAL = 2

# about states :D
# DRILLING → well is drilling normally
# CONNECTION → temporarily stopping, ROP = 0
# CIRCULATING → circulating mud, ROP = 0, low RPM


# initialization 
well_info = {}
base_depths = {"Well-01": 1500.0, "Well-02": 2200.0, "Well-03": 3100.0}
for w in WELLS:
    well_info[w] = {
        "state": "DRILLING",
        "timer": random.randint(5,15),
        "depth": base_depths[w],
        "v_depth": base_depths[w] - 10.0,
        "rpm": 120.0,
        "rop": random.uniform(2,5),
        "swob": 15.0,
        "hkld": 220.0,
        "flow": 1000.0,
        "sppa": 3000.0,
        "spm1": 60.0,
        "spm2": 54.0,
        "total_strokes": 100000,
        "time_on_bottom": 120.0
    }

# to avoid big 'jumps' 
def smooth(value, target, max_change):
    delta = target - value
    if abs(delta) > max_change:
        delta = max_change if delta > 0 else -max_change
    return value + delta

try:
    while True:
        data_points = []

        for well, info in well_info.items():
            # update state - makes wells change state over time, like real rigs switching between drilling, connecting, circulating.
            info["timer"] -= 1
            if info["timer"] <= 0:
                info["state"] = random.choice(STATES)
                info["timer"] = random.randint(5,15)

            state = info["state"]

            # targets per state
            if state == "DRILLING":
                target_rpm = random.uniform(100,140)
                target_swob = random.uniform(14,18)
                target_rop = target_rpm*0.12 + target_swob*0.4 + random.uniform(0,2)                
                target_hkld = 220 - target_swob
                target_flow = random.uniform(900,1100)
                target_sppa = random.uniform(2800,3200)
                actc = 1
            elif state == "CONNECTION":
                target_rpm = target_swob = target_rop = target_hkld = target_flow = 0.0
                target_sppa = random.uniform(50,150)
                actc = 4
            else: # CIRCULATING
                target_rpm = random.uniform(30,50)
                target_swob = 2.0
                target_rop = 0.0
                target_hkld = 170.0
                target_flow = random.uniform(600,800)
                target_sppa = random.uniform(1500,2000)
                actc = 2

            # smooth updates
            info["rpm"] = smooth(info["rpm"], target_rpm, 2.0)
            info["swob"] = smooth(info["swob"], target_swob, 0.2)
            # rop only exists when drilling
            if state == "DRILLING":
                info["rop"] = smooth(info["rop"], target_rop, 1.0)
            else:
                info["rop"] = 0.0            
            info["hkld"] = smooth(info["hkld"], target_hkld, 1.0)
            info["flow"] = smooth(info["flow"], target_flow, 10.0)
            info["sppa"] = smooth(info["sppa"], target_sppa, 20.0)

            # depth
            if state == "DRILLING":
                info["depth"] += info["rop"] * INTERVAL / 3600
                info["v_depth"] += info["rop"] * INTERVAL / 3600 * 0.99

            # pumps & strokes
            spm = info["flow"]/9.5
            info["spm1"] = spm
            info["spm2"] = spm*0.9
            info["spm3"] = 0.0
            info["total_strokes"] += int(spm/60*INTERVAL)
            if state=="DRILLING":
                info["time_on_bottom"] += INTERVAL/60

            # gas
            g_c1 = 0.5 + info["rop"]*0.02 + random.uniform(0,0.2)
            g_c2 = 0.05 + info["rop"]*0.005 + random.uniform(0,0.01)
            g_c3 = 0.01 + info["rop"]*0.002 + random.uniform(0,0.005)
            gasa = g_c1 + g_c2 + g_c3 # total gas

            # combining all vars into a dictionary
            dp = {
                "timestamp": int(time.time()), # unix timestamp easier to work witk later             
                "well_id": well,
                "state": state,
                "GS_ROP": round(info["rop"],2),
                "GS_RPM": round(info["rpm"],1),
                "GS_TQA": round(info["rpm"]*15 + info["rop"]*10,1),
                "GS_SWOB": round(info["swob"],2),
                "GS_SWOBF": round(info["swob"],2),
                "GS_HKLD": round(info["hkld"],2),
                "GS_HKLDF": round(info["hkld"],2),
                "GS_BPOS": round(random.uniform(0,30),2),
                "DBTM": round(info["depth"],2),
                "GS_DBTM": round(info["depth"],2),
                "GS_DBTV": round(info["v_depth"],2),
                "GS_DMEA": round(info["depth"],2),
                "GS_DVER": round(info["v_depth"],2),
                "GS_TFLO": round(info["flow"],1),
                "GS_MFOA": round(info["flow"]*0.95,1),
                "GS_MFOP": round(random.uniform(90,98),1) if info["flow"]>0 else 0.0,
                "GS_SPPA": round(info["sppa"],1),
                "GS_CPPA": round(random.uniform(100,500),1),
                "GS_MWTI": 1250.0,
                "GS_MDOA": 1260.0,
                "GS_CHKP": round(random.uniform(0,5),1) if state != "DRILLING" else 0.0,
                "GS_KILP": 0.0,
                "GS_WHP": round(info["sppa"]*0.8,1),
                "ACTC": actc,
                "GS_ACTC": actc,
                "GS_MTOA": round(info["time_on_bottom"],2),
                "MSP1": random.randint(0,1),
                "MSP2": random.randint(0,1),
                "GS_SPM1": round(info["spm1"],1),
                "GS_SPM2": round(info["spm2"],1),
                "GS_SPM3": round(info["spm3"],1),
                "GS_TSTK": info["total_strokes"],
                "GS_G_C1": round(g_c1,3),
                "GS_G_C2": round(g_c2,3),
                "GS_G_C3": round(g_c3,3),
                "GS_G_IC4": 0.01, "GS_G_NC4":0.01, "GS_G_IC5":0.005, "GS_G_NC5":0.005,
                "GS_GASA": round(gasa,3),
                "GS_TV01": 15000, "GS_TV02": 15000, "GS_TTV1":45000,
                "GS_TVA":60000, "GS_TVCA":10000
            }
            data_points.append(dp)

        # send dat
        points = []
        for dp in data_points:
            point = {
                "measurement": "drilling",
                "tags": {"well_id": dp["well_id"], "state": dp["state"]},
                "fields": {k: v for k, v in dp.items() 
                    if k not in ["timestamp", "well_id", "state"]}
            }
            points.append(point)
        client.write_points(points)

except KeyboardInterrupt:
    print("\nSimulation stopped.")