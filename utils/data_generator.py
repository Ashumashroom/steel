"""
Synthetic data generator for the Steel Plant Maintenance Wizard.
Generates manuals, SOPs, logs, sensor data, and spare parts inventory.
"""
import os, csv, json, random
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DATA_DIR, MANUALS_DIR, SOPS_DIR, LOGS_DIR, SENSOR_DIR,
    SPARE_PARTS_DIR, EQUIPMENT, SENSOR_PARAMS, SENSOR_RANGES,
)


# ─── Equipment Manual Templates ──────────────────────────────
MANUAL_TEMPLATES = {
    "Blast Furnace": """# Blast Furnace — Equipment Manual
## Equipment ID: {eid}  |  Name: {name}

### 1. Overview
The blast furnace is the primary iron-making unit. It reduces iron ore to molten pig iron using coke as fuel and limestone as flux. Operating temperature ranges from 1100°C to 1500°C.

### 2. Key Components
- **Furnace Shell**: Steel plate with refractory lining (carbon/alumina bricks)
- **Tuyeres**: 20-32 water-cooled copper nozzles injecting hot blast air
- **Cooling System**: Stave coolers with closed-loop water circuit; inlet 28°C, outlet max 45°C
- **Top Charging System**: Bell-less top (Paul Wurth type) with rotating chute
- **Gas Cleaning Plant**: Dust catcher → cyclone → scrubber → electrostatic precipitator
- **Cast House**: Tap holes, runners, torpedo ladles

### 3. Normal Operating Parameters
| Parameter | Normal Range | Alarm | Trip |
|-----------|-------------|-------|------|
| Hearth Temperature | 1150-1300°C | >1350°C | >1450°C |
| Blast Pressure | 2.0-3.0 bar | >3.5 bar | >4.0 bar |
| Top Gas Temp | 100-250°C | >300°C | >400°C |
| Cooling Water ΔT | 5-10°C | >15°C | >20°C |
| Vibration (shell) | 1.5-3.5 mm/s | >5.0 mm/s | >8.0 mm/s |

### 4. Common Failure Modes
1. **Hearth Erosion**: Gradual wear of refractory lining; detected via thermocouple trends
2. **Tuyere Burnout**: Cooling water leak into furnace; sudden temperature spike + steam
3. **Hanging / Slipping**: Burden material sticks then collapses; pressure fluctuations
4. **Cooling System Leak**: Rising water temperature differential; reduced flow
5. **Gas Leak**: CO detection at shell joints; pressure drop in top gas system

### 5. Preventive Maintenance Schedule
| Task | Frequency | Duration |
|------|-----------|----------|
| Tuyere inspection | Weekly | 2 hours |
| Cooling water chemistry check | Daily | 30 min |
| Refractory thickness measurement | Monthly | 4 hours |
| Gas cleaning plant overhaul | Quarterly | 8 hours |
| Full reline (campaign end) | 10-15 years | 3-6 months |

### 6. Emergency Procedures
- **Tuyere Burnout**: Immediately plug affected tuyere, reduce blast volume, notify shift supervisor
- **Burden Hanging**: Reduce blast pressure gradually, do NOT increase suddenly
- **Cooling Failure**: Switch to backup pump within 60 seconds; prepare for controlled shutdown if backup fails
""",
    "BOF": """# Basic Oxygen Furnace (BOF) — Equipment Manual
## Equipment ID: {eid}  |  Name: {name}

### 1. Overview
The BOF converts molten pig iron into steel by blowing high-purity oxygen through a top-mounted lance. Heat cycle: 35-45 minutes per heat.

### 2. Key Components
- **Vessel**: Pear-shaped steel shell with MgO-C refractory lining (300-500 heats life)
- **Oxygen Lance**: Water-cooled, 4-5 nozzle tip; flow rate 500-700 Nm³/min
- **Trunnion Ring & Tilting Mechanism**: Hydraulic tilting for charging and tapping
- **Gas Recovery Hood**: Captures CO-rich off-gas for energy recovery
- **Alloy & Flux Addition System**: Bins, weigh hoppers, and chutes

### 3. Normal Operating Parameters
| Parameter | Normal Range | Alarm | Trip |
|-----------|-------------|-------|------|
| Bath Temperature | 1600-1700°C | >1720°C | >1750°C |
| Oxygen Flow | 500-700 Nm³/min | >750 | >800 |
| Vessel Pressure | 1.5-2.0 bar | >2.5 bar | >3.0 bar |
| Lance Vibration | 2.0-4.0 mm/s | >6.0 mm/s | >10 mm/s |
| Cooling Water Temp | 30-40°C | >50°C | >60°C |

### 4. Common Failure Modes
1. **Refractory Wear**: Accelerated by high FeO slag; vessel profile changes
2. **Lance Tip Erosion**: Nozzle blockage or burnthrough; oxygen distribution affected
3. **Trunnion Bearing Failure**: Overheating, vibration increase; tilting becomes sluggish
4. **Slopping**: Excessive foam ejection; loss of material and safety hazard
5. **Tap Hole Blockage**: Skull formation; delayed tapping

### 5. Preventive Maintenance Schedule
| Task | Frequency | Duration |
|------|-----------|----------|
| Vessel profile scan | Every 50 heats | 1 hour |
| Lance tip inspection | Every 100 heats | 2 hours |
| Trunnion bearing grease | Weekly | 1 hour |
| Hood & ductwork inspection | Monthly | 4 hours |
| Full reline | Every 300-500 heats | 3-5 days |

### 6. Emergency Procedures
- **Slopping**: Reduce oxygen flow immediately, raise lance height, add coolant
- **Lance Cooling Failure**: Retract lance immediately, switch to backup water supply
- **Vessel Tilt Failure**: Engage manual hydraulic override; do NOT attempt electrical reset
""",
    "Rolling Mill": """# Rolling Mill — Equipment Manual
## Equipment ID: {eid}  |  Name: {name}

### 1. Overview
Rolling mills reduce steel slab/billet thickness through progressive passes between work rolls. Hot rolling operates at 900-1250°C; cold rolling at ambient temperature.

### 2. Key Components
- **Work Rolls**: High-chrome or HSS rolls; surface hardness 65-85 Shore C
- **Backup Rolls**: Forged steel; support work rolls against deflection
- **Main Drive Motor**: DC/AC motor 3000-8000 kW; connected via spindles and couplings
- **Hydraulic AGC**: Automatic gauge control for thickness precision (±0.01mm)
- **Lubrication System**: Circulating oil system; tank 5000-15000L; filtration to 10μm
- **Roll Cooling**: Water spray headers; 200-500 L/min per roll

### 3. Normal Operating Parameters
| Parameter | Normal Range | Alarm | Trip |
|-----------|-------------|-------|------|
| Roll Temperature | 300-400°C (hot) | >450°C | >500°C |
| Motor Vibration | 2.5-5.0 mm/s | >7.0 mm/s | >12.0 mm/s |
| Motor RPM | 1100-1300 | >1400 | >1500 |
| Oil Pressure | 40-50 bar | <35 bar | <30 bar |
| Motor Current | 340-420 A | >460 A | >500 A |

### 4. Common Failure Modes
1. **Bearing Failure**: Inner/outer race spalling; increased vibration at specific frequencies
2. **Roll Surface Defect**: Spalling, firecracks; causes product surface defects
3. **Gear Coupling Wear**: Misalignment; vibration + noise increase
4. **Motor Overheating**: Insulation degradation; current imbalance
5. **Oil System Contamination**: Particle count increase; filter ΔP rise

### 5. Preventive Maintenance Schedule
| Task | Frequency | Duration |
|------|-----------|----------|
| Vibration monitoring | Weekly | 2 hours |
| Oil sample analysis | Bi-weekly | 1 hour |
| Roll surface inspection | After each campaign | 3 hours |
| Bearing replacement | Condition-based | 8-16 hours |
| Full mill overhaul | Annual | 5-7 days |
""",
    "Caster": """# Continuous Caster — Equipment Manual
## Equipment ID: {eid}  |  Name: {name}

### 1. Overview
The continuous caster transforms liquid steel into solid slabs/billets. Molten steel flows from a ladle through a tundish into an oscillating water-cooled mold.

### 2. Key Components
- **Tundish**: Refractory-lined vessel; buffer capacity 20-40 tonnes
- **Mold**: Copper plates with Ni-Cr coating; oscillation frequency 60-200 cpm
- **Secondary Cooling**: Spray zones with air-mist nozzles; 6-12 zones
- **Withdrawal Rolls**: Driven rolls pulling the solidifying strand
- **Torch Cutting Machine**: Oxy-fuel cutting to desired slab length

### 3. Normal Operating Parameters
| Parameter | Normal Range | Alarm | Trip |
|-----------|-------------|-------|------|
| Mold Temperature | 1520-1560°C | >1580°C | >1600°C |
| Casting Speed | 1.0-1.4 m/min | >1.6 | >1.8 |
| Mold Level | 72-78% | <65% or >85% | <55% or >90% |
| Cooling Water Flow | 800-900 L/min | <700 | <600 |

### 4. Common Failure Modes
1. **Breakout**: Solidified shell rupture; molten steel spill (critical safety hazard)
2. **Mold Sticking**: Inadequate lubrication; friction increase detected by thermocouples
3. **Nozzle Clogging**: Alumina buildup in submerged entry nozzle
4. **Roll Misalignment**: Strand surface cracks; bulging between rolls
5. **Tundish Nozzle Erosion**: Increased steel flow variation

### 5. Emergency Procedures
- **Breakout Detection**: System auto-reduces casting speed; operator confirms emergency stop
- **Mold Level Loss**: Immediately close slide gate; initiate tundish drain procedure
""",
    "Ladle Furnace": """# Ladle Furnace — Equipment Manual
## Equipment ID: {eid}  |  Name: {name}

### 1. Overview
The ladle furnace performs secondary steelmaking: temperature adjustment, desulfurization, alloying, and inclusion removal via argon stirring and electric arc heating.

### 2. Key Components
- **Electrodes**: 3-phase graphite electrodes; diameter 300-500mm
- **Roof**: Water-cooled delta or eccentric bottom tapping design
- **Argon Stirring**: Porous plug in ladle bottom; 5-15 Nm³/h flow
- **Wire Feeding**: CaSi, CaFe, Al wires for micro-alloying
- **Alloy Hopper System**: 8-12 bins for ferro-alloys and fluxes

### 3. Normal Operating Parameters
| Parameter | Normal Range | Alarm | Trip |
|-----------|-------------|-------|------|
| Steel Temperature | 1550-1620°C | >1650°C | >1680°C |
| Arc Voltage | 230-270 V | >290 V | >310 V |
| Electrode Current | 30-40 kA | >45 kA | >50 kA |
| Argon Pressure | 0.4-0.6 bar | >0.8 bar | >1.0 bar |

### 4. Common Failure Modes
1. **Electrode Breakage**: Mechanical shock or thermal stress; production delay
2. **Ladle Refractory Failure**: Slag line erosion; steel leakage risk
3. **Porous Plug Blockage**: Reduced stirring efficiency; inclusion removal degraded
4. **Hydraulic Roof Lift Failure**: Cannot open/close roof; heat loss
5. **Water Leak in Roof**: Steam explosion risk; immediate shutdown required
""",
}


# ─── SOP Templates ────────────────────────────────────────────
SOP_TEMPLATES = {
    "Bearing Replacement": """# SOP: Bearing Replacement Procedure
## Applicable Equipment: Rolling Mill Motors, Caster Withdrawal Rolls

### Safety Requirements
- Lock-Out Tag-Out (LOTO) mandatory
- Minimum 2 technicians required
- PPE: heat-resistant gloves, safety glasses, steel-toe boots

### Procedure
1. De-energize equipment and apply LOTO
2. Disconnect coupling from drive side
3. Remove bearing housing end caps
4. Use hydraulic puller to extract old bearing
5. Inspect shaft journal for wear/scoring (tolerance ±0.02mm)
6. Clean housing bore and shaft with solvent
7. Heat new bearing to 80°C using induction heater
8. Slide bearing onto shaft — DO NOT hammer
9. Allow bearing to cool and self-seat (minimum 30 min)
10. Apply recommended grease (Mobilith SHC 220) — fill to 40% capacity
11. Reassemble housing, torque bolts to specification
12. Rotate shaft by hand — check for smooth operation
13. Remove LOTO, perform test run at low speed for 15 minutes
14. Check vibration and temperature after 1 hour of normal operation

### Acceptance Criteria
- Vibration < 4.5 mm/s RMS at bearing housing
- Temperature rise < 30°C above ambient after 2 hours
- No abnormal noise
""",
    "Cooling System Maintenance": """# SOP: Cooling Water System Maintenance
## Applicable Equipment: Blast Furnace, BOF, Caster Mold

### Safety Requirements
- Isolate water supply before opening any piping
- Verify zero pressure before removing flanges
- Chemical handling PPE for water treatment chemicals

### Procedure
1. Check water chemistry: pH 7.5-8.5, conductivity <500 μS/cm, hardness <100 ppm
2. Inspect strainer/filters — clean or replace if ΔP > 0.5 bar
3. Check pump performance: flow rate, discharge pressure, vibration
4. Inspect heat exchangers for fouling — clean tubes if approach temp > 5°C
5. Check cooling tower fill for biological growth — treat if necessary
6. Verify all safety valves are functional — test annually
7. Inspect piping for corrosion, leaks, and scaling
8. Check make-up water dosing system: inhibitor and biocide levels
9. Record all readings in maintenance log

### Frequency
- Daily: Visual inspection, pump parameters, water chemistry
- Weekly: Filter cleaning, tower inspection
- Monthly: Full system audit with detailed report
""",
    "Emergency Shutdown": """# SOP: Emergency Shutdown Procedure
## Applicable Equipment: All Critical Equipment

### Trigger Conditions
- Equipment trip alarm activation
- Abnormal vibration exceeding 2x normal baseline
- Cooling system failure with no backup available
- Structural crack or fracture detected
- Fire or explosion hazard identified

### Procedure
1. Press EMERGENCY STOP button at local panel
2. Notify shift supervisor and control room immediately
3. Verify all energy sources are isolated (electrical, hydraulic, pneumatic, thermal)
4. Apply LOTO on all isolation points
5. Evacuate personnel from hazard zone (minimum 10m radius)
6. Activate fire suppression if fire detected
7. Document time, conditions, and actions taken
8. Do NOT attempt restart until root cause is identified and corrected
9. Restart requires written authorization from maintenance manager

### Post-Shutdown Checklist
- [ ] Incident report filed within 2 hours
- [ ] Equipment inspection completed
- [ ] Root cause analysis initiated
- [ ] Corrective action plan developed
- [ ] Safety review conducted before restart
""",
}


# ─── Failure Modes for Log Generation ─────────────────────────
FAULT_CODES = {
    "Blast Furnace": [
        ("BF-F001", "Tuyere burnout", "critical"),
        ("BF-F002", "Cooling water leak", "high"),
        ("BF-F003", "Burden hanging", "high"),
        ("BF-F004", "Hearth erosion detected", "critical"),
        ("BF-F005", "Gas leak at top seal", "medium"),
        ("BF-F006", "Charging system malfunction", "medium"),
        ("BF-F007", "Dust catcher overflow", "low"),
    ],
    "BOF": [
        ("BOF-F001", "Refractory hot spot", "critical"),
        ("BOF-F002", "Lance tip erosion", "high"),
        ("BOF-F003", "Trunnion bearing overheating", "high"),
        ("BOF-F004", "Slopping event", "medium"),
        ("BOF-F005", "Tap hole blockage", "medium"),
        ("BOF-F006", "Hood duct damage", "low"),
    ],
    "Rolling Mill": [
        ("RM-F001", "Main motor bearing failure", "critical"),
        ("RM-F002", "Gear coupling misalignment", "high"),
        ("RM-F003", "Roll surface spalling", "high"),
        ("RM-F004", "Hydraulic oil contamination", "medium"),
        ("RM-F005", "Motor insulation degradation", "high"),
        ("RM-F006", "AGC calibration drift", "low"),
        ("RM-F007", "Coolant nozzle blockage", "low"),
    ],
    "Caster": [
        ("CC-F001", "Breakout event", "critical"),
        ("CC-F002", "Mold sticking detected", "high"),
        ("CC-F003", "SEN clogging", "high"),
        ("CC-F004", "Roll misalignment", "medium"),
        ("CC-F005", "Tundish nozzle erosion", "medium"),
        ("CC-F006", "Spray nozzle blockage", "low"),
    ],
    "Ladle Furnace": [
        ("LF-F001", "Electrode breakage", "high"),
        ("LF-F002", "Ladle refractory failure", "critical"),
        ("LF-F003", "Porous plug blockage", "medium"),
        ("LF-F004", "Roof water leak", "critical"),
        ("LF-F005", "Hydraulic roof lift failure", "medium"),
    ],
}

ACTIONS_TAKEN = [
    "Replaced damaged component", "Performed emergency repair",
    "Adjusted operating parameters", "Cleaned and flushed system",
    "Applied temporary fix; permanent repair scheduled",
    "Replaced bearing assembly", "Recalibrated sensors",
    "Conducted hot repair of refractory", "Replaced cooling element",
    "Tightened connections and re-sealed", "Replaced filter cartridge",
    "Realigned coupling assembly", "Applied weld overlay repair",
]


# ─── Spare Parts Data ─────────────────────────────────────────
SPARE_PARTS = [
    ("SP-001", "Tuyere Assembly", "BF-001", 8, 14, 45000, "TataSteel Spares"),
    ("SP-002", "Cooling Stave Panel", "BF-001", 4, 30, 120000, "Paul Wurth"),
    ("SP-003", "SKF 23060 Bearing", "RM-001", 6, 7, 8500, "SKF India"),
    ("SP-004", "Hydraulic Pump (Rexroth A10V)", "RM-001", 2, 21, 65000, "Bosch Rexroth"),
    ("SP-005", "Oxygen Lance Tip (5-nozzle)", "BOF-001", 12, 5, 15000, "Danieli"),
    ("SP-006", "MgO-C Brick (BOF lining)", "BOF-001", 500, 10, 850, "RHI Magnesita"),
    ("SP-007", "Copper Mold Plate", "CC-001", 4, 28, 180000, "SMS Concast"),
    ("SP-008", "SEN (Submerged Entry Nozzle)", "CC-001", 20, 3, 2500, "Vesuvius"),
    ("SP-009", "Graphite Electrode (500mm)", "LF-001", 6, 10, 35000, "Graphite India"),
    ("SP-010", "Porous Plug", "LF-001", 10, 5, 4500, "TYK Corporation"),
    ("SP-011", "Coupling Gear Sleeve", "RM-002", 4, 14, 22000, "Renk Group"),
    ("SP-012", "HSS Work Roll", "RM-001", 2, 45, 350000, "Akers Sweden"),
    ("SP-013", "Thermocouple (Type K)", "BF-001", 50, 2, 450, "Tempsens India"),
    ("SP-014", "Vibration Sensor (ICP)", "RM-001", 10, 3, 1200, "PCB Piezotronics"),
    ("SP-015", "Oil Filter Element (10μm)", "RM-001", 30, 1, 350, "Pall Corporation"),
]


def generate_all():
    """Generate all synthetic data files."""
    _ensure_dirs()
    _generate_manuals()
    _generate_sops()
    _generate_maintenance_logs()
    _generate_sensor_data()
    _generate_spare_parts()
    _generate_failure_reports()
    print("✅ All synthetic data generated successfully!")


def _ensure_dirs():
    for d in [MANUALS_DIR, SOPS_DIR, LOGS_DIR, SENSOR_DIR, SPARE_PARTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def _generate_manuals():
    for eid, info in EQUIPMENT.items():
        etype = info["type"]
        if etype in MANUAL_TEMPLATES:
            content = MANUAL_TEMPLATES[etype].format(eid=eid, name=info["name"])
            path = MANUALS_DIR / f"{eid}_manual.md"
            path.write_text(content, encoding="utf-8")
    print(f"  📖 Generated {len(EQUIPMENT)} equipment manuals")


def _generate_sops():
    for title, content in SOP_TEMPLATES.items():
        filename = title.lower().replace(" ", "_") + ".md"
        (SOPS_DIR / filename).write_text(content, encoding="utf-8")
    print(f"  📋 Generated {len(SOP_TEMPLATES)} SOPs")


def _generate_maintenance_logs():
    random.seed(42)
    rows = []
    base_date = datetime(2024, 1, 1)
    for _ in range(500):
        eid = random.choice(list(EQUIPMENT.keys()))
        etype = EQUIPMENT[eid]["type"]
        faults = FAULT_CODES.get(etype, [])
        if not faults:
            continue
        code, desc, severity = random.choice(faults)
        ts = base_date + timedelta(
            days=random.randint(0, 545),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        rows.append({
            "timestamp": ts.isoformat(),
            "equipment_id": eid,
            "fault_code": code,
            "description": desc,
            "severity": severity,
            "action_taken": random.choice(ACTIONS_TAKEN),
            "downtime_hours": round(random.uniform(0.5, 72), 1),
            "technician": f"Tech-{random.randint(100,999)}",
        })
    df = pd.DataFrame(rows).sort_values("timestamp")
    df.to_csv(LOGS_DIR / "maintenance_logs.csv", index=False)
    print(f"  📝 Generated {len(df)} maintenance log entries")


def _generate_sensor_data():
    np.random.seed(42)
    for eid, info in EQUIPMENT.items():
        etype = info["type"]
        params = SENSOR_PARAMS.get(etype, [])
        ranges = SENSOR_RANGES.get(etype, {})
        if not params:
            continue
        n_points = 2000
        timestamps = pd.date_range("2024-06-01", periods=n_points, freq="15min")
        data = {"timestamp": timestamps, "equipment_id": eid}
        for p in params:
            mean, std = ranges.get(p, (100, 10))
            values = np.random.normal(mean, std, n_points)
            # Inject anomalies (5% of data)
            anomaly_idx = np.random.choice(n_points, size=int(n_points * 0.05), replace=False)
            values[anomaly_idx] += np.random.choice([-1, 1], size=len(anomaly_idx)) * std * np.random.uniform(3, 6, len(anomaly_idx))
            # Inject degradation trend in last 20%
            degradation_start = int(n_points * 0.8)
            trend = np.linspace(0, std * 2, n_points - degradation_start)
            values[degradation_start:] += trend
            data[p] = np.round(values, 2)
        df = pd.DataFrame(data)
        df.to_csv(SENSOR_DIR / f"{eid}_sensors.csv", index=False)
    print(f"  📊 Generated sensor data for {len(EQUIPMENT)} equipment units")


def _generate_spare_parts():
    rows = []
    for part in SPARE_PARTS:
        rows.append({
            "part_id": part[0], "part_name": part[1], "equipment_id": part[2],
            "quantity_in_stock": part[3], "lead_time_days": part[4],
            "unit_cost_inr": part[5], "supplier": part[6],
        })
    df = pd.DataFrame(rows)
    df.to_csv(SPARE_PARTS_DIR / "spare_parts_inventory.csv", index=False)
    print(f"  🔧 Generated {len(df)} spare parts entries")


def _generate_failure_reports():
    random.seed(123)
    reports = []
    for i in range(15):
        eid = random.choice(list(EQUIPMENT.keys()))
        etype = EQUIPMENT[eid]["type"]
        faults = FAULT_CODES.get(etype, [])
        if not faults:
            continue
        code, desc, severity = random.choice(faults)
        report = f"""# Failure Analysis Report — FAR-{2024000 + i}
## Equipment: {EQUIPMENT[eid]['name']} ({eid})
## Date: {datetime(2024, random.randint(1,12), random.randint(1,28)).strftime('%Y-%m-%d')}
## Severity: {severity.upper()}

### 1. Incident Summary
Fault code **{code}** was triggered on {eid}. The issue was identified as: **{desc}**.
The equipment was operating under normal load conditions when the anomaly was first detected
by the monitoring system. Maintenance team responded within 45 minutes.

### 2. Root Cause
After detailed investigation, the root cause was determined to be:
- Accelerated wear due to operating beyond recommended duty cycle
- Contributing factor: delayed preventive maintenance (overdue by 2 weeks)
- Environmental factor: high ambient temperature (>45°C) during summer months

### 3. Corrective Actions
1. Immediate: {random.choice(ACTIONS_TAKEN)}
2. Short-term: Schedule comprehensive inspection within 7 days
3. Long-term: Revise maintenance interval from quarterly to bi-monthly

### 4. Recommendations
- Install additional monitoring sensors for early detection
- Update maintenance SOP to include pre-summer inspection checklist
- Stock critical spare parts for faster turnaround
"""
        reports.append(report)
        path = LOGS_DIR / f"failure_report_FAR_{2024000 + i}.md"
        path.write_text(report, encoding="utf-8")
    print(f"  🔍 Generated {len(reports)} failure analysis reports")


if __name__ == "__main__":
    generate_all()
