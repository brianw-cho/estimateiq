"""
Synthetic Data Generator for EstimateIQ Prototype

This script generates:
1. 100 historical work orders with realistic marine service data
2. 300 parts catalog entries for common marine parts
3. Labor rates configuration

Run with: python scripts/seed_data.py
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import uuid

# Ensure reproducible results
random.seed(42)

# Output directory
DATA_DIR = Path(__file__).parent.parent / "app" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Configuration Data
# ============================================================================

VESSEL_TYPES = [
    {"type": "Runabout", "loa_min": 18, "loa_max": 24},
    {"type": "Cabin Cruiser", "loa_min": 25, "loa_max": 35},
    {"type": "Center Console", "loa_min": 20, "loa_max": 30},
    {"type": "Sailboat", "loa_min": 25, "loa_max": 40},
    {"type": "Pontoon Boat", "loa_min": 20, "loa_max": 26},
]

ENGINE_CONFIGS = [
    {"make": "Mercury", "models": ["150 FourStroke", "200 Verado", "250 Pro XS", "300 Verado", "115 FourStroke"]},
    {"make": "Yamaha", "models": ["F150", "F200", "F250", "F300", "F115", "F90"]},
    {"make": "Volvo Penta", "models": ["D4-300", "D6-370", "D4-260", "D3-200", "5.7L GXi"]},
    {"make": "MerCruiser", "models": ["4.3L MPI", "5.0L MPI", "6.2L MPI", "350 MAG", "8.2L MAG"]},
    {"make": "Suzuki", "models": ["DF150", "DF200", "DF250", "DF300", "DF115"]},
    {"make": "Honda", "models": ["BF150", "BF200", "BF250", "BF115", "BF90"]},
]

SERVICE_CATEGORIES = [
    {
        "category": "engine",
        "services": [
            {"desc": "Oil and filter change", "hours_range": (1.0, 2.0), "parts": ["oil_filter", "engine_oil"]},
            {"desc": "Full engine tune-up", "hours_range": (2.5, 4.0), "parts": ["spark_plugs", "fuel_filter", "oil_filter", "engine_oil"]},
            {"desc": "Engine diagnostic and inspection", "hours_range": (1.5, 3.0), "parts": []},
            {"desc": "Timing belt replacement", "hours_range": (3.0, 5.0), "parts": ["timing_belt", "tensioner"]},
            {"desc": "Thermostat replacement", "hours_range": (1.5, 2.5), "parts": ["thermostat", "gasket"]},
        ]
    },
    {
        "category": "hull",
        "services": [
            {"desc": "Hull cleaning and bottom paint", "hours_range": (4.0, 8.0), "parts": ["bottom_paint", "primer"]},
            {"desc": "Gelcoat repair", "hours_range": (2.0, 4.0), "parts": ["gelcoat", "fiberglass_mat"]},
            {"desc": "Hull inspection and cleaning", "hours_range": (1.0, 2.0), "parts": []},
            {"desc": "Zinc anode replacement", "hours_range": (1.0, 2.0), "parts": ["zincs"]},
            {"desc": "Through-hull fitting service", "hours_range": (2.0, 4.0), "parts": ["thru_hull", "sealant"]},
        ]
    },
    {
        "category": "electrical",
        "services": [
            {"desc": "Battery replacement and testing", "hours_range": (0.5, 1.5), "parts": ["battery"]},
            {"desc": "Navigation electronics installation", "hours_range": (2.0, 4.0), "parts": ["wiring", "connectors"]},
            {"desc": "Electrical troubleshooting", "hours_range": (1.5, 3.0), "parts": ["fuses", "wiring"]},
            {"desc": "Bilge pump installation", "hours_range": (1.0, 2.0), "parts": ["bilge_pump", "wiring"]},
            {"desc": "LED lighting upgrade", "hours_range": (1.5, 3.0), "parts": ["led_lights", "wiring"]},
        ]
    },
    {
        "category": "mechanical",
        "services": [
            {"desc": "Steering system service", "hours_range": (2.0, 4.0), "parts": ["steering_fluid", "seals"]},
            {"desc": "Trim system repair", "hours_range": (1.5, 3.0), "parts": ["trim_fluid", "seals"]},
            {"desc": "Hydraulic system service", "hours_range": (2.0, 3.5), "parts": ["hydraulic_fluid", "seals"]},
            {"desc": "Control cable replacement", "hours_range": (2.0, 3.0), "parts": ["control_cable"]},
            {"desc": "Throttle and shift adjustment", "hours_range": (1.0, 2.0), "parts": []},
        ]
    },
    {
        "category": "outboard",
        "services": [
            {"desc": "Impeller replacement", "hours_range": (1.5, 2.5), "parts": ["impeller", "gasket"]},
            {"desc": "Lower unit service", "hours_range": (2.0, 3.5), "parts": ["gear_oil", "seals", "gasket"]},
            {"desc": "Propeller inspection and service", "hours_range": (0.5, 1.5), "parts": ["prop_hardware"]},
            {"desc": "Annual outboard service", "hours_range": (3.0, 5.0), "parts": ["impeller", "gear_oil", "spark_plugs", "fuel_filter", "oil_filter"]},
            {"desc": "Powerhead inspection", "hours_range": (1.5, 2.5), "parts": []},
        ]
    },
    {
        "category": "inboard",
        "services": [
            {"desc": "Transmission service", "hours_range": (2.0, 3.5), "parts": ["trans_fluid", "filter"]},
            {"desc": "Shaft and seal service", "hours_range": (2.5, 4.0), "parts": ["shaft_seal", "packing"]},
            {"desc": "Exhaust system inspection", "hours_range": (1.0, 2.0), "parts": ["exhaust_gasket"]},
            {"desc": "Raw water pump rebuild", "hours_range": (1.5, 2.5), "parts": ["impeller", "seals", "gasket"]},
            {"desc": "Engine alignment check", "hours_range": (1.5, 2.5), "parts": []},
        ]
    },
    {
        "category": "annual",
        "services": [
            {"desc": "Spring commissioning", "hours_range": (4.0, 8.0), "parts": ["oil_filter", "engine_oil", "fuel_filter", "impeller"]},
            {"desc": "Winterization", "hours_range": (2.5, 4.5), "parts": ["antifreeze", "fuel_stabilizer", "fogging_oil"]},
            {"desc": "Annual service package", "hours_range": (4.0, 6.0), "parts": ["oil_filter", "engine_oil", "fuel_filter", "spark_plugs"]},
            {"desc": "Pre-purchase survey prep", "hours_range": (2.0, 4.0), "parts": []},
            {"desc": "Season-end inspection", "hours_range": (1.5, 2.5), "parts": []},
        ]
    },
    {
        "category": "diagnostic",
        "services": [
            {"desc": "No-start troubleshooting", "hours_range": (1.5, 3.0), "parts": []},
            {"desc": "Overheating diagnosis", "hours_range": (1.0, 2.5), "parts": []},
            {"desc": "Oil leak diagnosis", "hours_range": (1.0, 2.0), "parts": []},
            {"desc": "Vibration analysis", "hours_range": (1.0, 2.0), "parts": []},
            {"desc": "Performance evaluation", "hours_range": (1.5, 2.5), "parts": []},
        ]
    },
]

REGIONS = ["Northeast", "Southeast", "Gulf Coast", "Great Lakes", "West Coast", "Pacific Northwest"]

SEASONS = ["spring", "summer", "fall", "winter"]


# ============================================================================
# Parts Catalog Generation
# ============================================================================

def generate_parts_catalog() -> List[Dict[str, Any]]:
    """Generate 300 marine parts for the catalog"""
    parts = []
    part_counter = 1000
    
    # Filters (30 items)
    filter_types = [
        ("Oil Filter", 28.99, 65.99),
        ("Fuel Filter", 18.99, 45.99),
        ("Air Filter", 22.99, 55.99),
        ("Fuel/Water Separator", 24.99, 75.99),
    ]
    for engine in ENGINE_CONFIGS:
        for filter_type, price_min, price_max in filter_types:
            if random.random() < 0.7:  # Not all engines have all filter types
                parts.append({
                    "part_number": f"FLT-{part_counter}",
                    "description": f"{engine['make']} {filter_type}",
                    "category": "Filters",
                    "compatible_engines": [engine["make"]],
                    "list_price": round(random.uniform(price_min, price_max), 2),
                    "unit": "each"
                })
                part_counter += 1
    
    # Engine oils (25 items)
    oil_types = [
        ("4-Stroke Engine Oil 10W-30", 28.99, 42.99, "quart"),
        ("4-Stroke Engine Oil 10W-40", 29.99, 44.99, "quart"),
        ("2-Stroke TC-W3 Oil", 18.99, 32.99, "quart"),
        ("Synthetic Blend 10W-30", 34.99, 52.99, "quart"),
        ("Full Synthetic 5W-30", 42.99, 64.99, "quart"),
        ("Diesel Engine Oil 15W-40", 32.99, 48.99, "gallon"),
    ]
    brands = ["Mercury", "Yamaha", "Quicksilver", "Pennzoil Marine", "Mobil 1"]
    for brand in brands:
        for oil_name, price_min, price_max, unit in oil_types:
            if random.random() < 0.6:
                parts.append({
                    "part_number": f"OIL-{part_counter}",
                    "description": f"{brand} {oil_name}",
                    "category": "Fluids",
                    "compatible_engines": [],  # Universal compatibility
                    "list_price": round(random.uniform(price_min, price_max), 2),
                    "unit": unit
                })
                part_counter += 1
    
    # Gear oils and lubricants (15 items)
    lube_types = [
        "Gear Lube (High Performance)",
        "Gear Lube (Standard)",
        "Hydraulic Trim Fluid",
        "Power Steering Fluid",
        "Grease Cartridge",
    ]
    for lube in lube_types:
        for brand in ["Mercury", "Yamaha", "Quicksilver"]:
            parts.append({
                "part_number": f"LUB-{part_counter}",
                "description": f"{brand} {lube}",
                "category": "Fluids",
                "compatible_engines": [],
                "list_price": round(random.uniform(12.99, 38.99), 2),
                "unit": "quart" if "Fluid" in lube else "each"
            })
            part_counter += 1
    
    # Spark plugs (35 items)
    for engine in ENGINE_CONFIGS:
        for model in engine["models"]:
            parts.append({
                "part_number": f"SPK-{part_counter}",
                "description": f"Spark Plug for {engine['make']} {model}",
                "category": "Ignition",
                "compatible_engines": [engine["make"]],
                "list_price": round(random.uniform(8.99, 24.99), 2),
                "unit": "each"
            })
            part_counter += 1
    
    # Impellers (20 items)
    for engine in ENGINE_CONFIGS:
        parts.append({
            "part_number": f"IMP-{part_counter}",
            "description": f"{engine['make']} Water Pump Impeller Kit",
            "category": "Impellers",
            "compatible_engines": [engine["make"]],
            "list_price": round(random.uniform(45.99, 125.99), 2),
            "unit": "kit"
        })
        part_counter += 1
        if random.random() < 0.5:
            parts.append({
                "part_number": f"IMP-{part_counter}",
                "description": f"{engine['make']} Impeller (Part Only)",
                "category": "Impellers",
                "compatible_engines": [engine["make"]],
                "list_price": round(random.uniform(28.99, 85.99), 2),
                "unit": "each"
            })
            part_counter += 1
    
    # Belts and hoses (30 items)
    belt_types = ["Serpentine Belt", "Alternator Belt", "Raw Water Hose", "Fuel Hose", "Exhaust Hose"]
    for engine in ENGINE_CONFIGS:
        for belt_type in belt_types:
            if random.random() < 0.5:
                parts.append({
                    "part_number": f"BLT-{part_counter}",
                    "description": f"{engine['make']} {belt_type}",
                    "category": "Belts & Hoses",
                    "compatible_engines": [engine["make"]],
                    "list_price": round(random.uniform(18.99, 89.99), 2),
                    "unit": "each" if "Belt" in belt_type else "foot"
                })
                part_counter += 1
    
    # Electrical (40 items)
    electrical_items = [
        ("Marine Battery 12V Group 24", 149.99, 249.99),
        ("Marine Battery 12V Group 27", 169.99, 289.99),
        ("Marine Battery 12V Group 31", 199.99, 349.99),
        ("Battery Terminal Kit", 12.99, 24.99),
        ("Battery Switch", 29.99, 89.99),
        ("Fuse Block 6-Way", 24.99, 49.99),
        ("Fuse Block 12-Way", 39.99, 79.99),
        ("Marine Wire 10 AWG (per foot)", 1.49, 2.99),
        ("Marine Wire 12 AWG (per foot)", 0.99, 1.99),
        ("Marine Wire 14 AWG (per foot)", 0.79, 1.49),
        ("Bilge Pump 500 GPH", 29.99, 59.99),
        ("Bilge Pump 1000 GPH", 49.99, 89.99),
        ("Float Switch", 14.99, 34.99),
        ("LED Navigation Light Set", 79.99, 199.99),
        ("Anchor Light", 29.99, 79.99),
    ]
    for item_name, price_min, price_max in electrical_items:
        parts.append({
            "part_number": f"ELC-{part_counter}",
            "description": item_name,
            "category": "Electrical",
            "compatible_engines": [],
            "list_price": round(random.uniform(price_min, price_max), 2),
            "unit": "each" if "foot" not in item_name else "foot"
        })
        part_counter += 1
        # Add variations
        if "Battery" in item_name and "Terminal" not in item_name:
            parts.append({
                "part_number": f"ELC-{part_counter}",
                "description": f"{item_name} (AGM)",
                "category": "Electrical",
                "compatible_engines": [],
                "list_price": round(random.uniform(price_min * 1.3, price_max * 1.3), 2),
                "unit": "each"
            })
            part_counter += 1
    
    # Bottom paint and primers (20 items)
    paint_brands = ["Interlux", "Pettit", "Sea Hawk", "West Marine"]
    paint_types = ["Ablative Bottom Paint", "Hard Bottom Paint", "Primer", "Gelcoat Repair Kit"]
    for brand in paint_brands:
        for paint_type in paint_types:
            parts.append({
                "part_number": f"PNT-{part_counter}",
                "description": f"{brand} {paint_type}",
                "category": "Bottom Paint",
                "compatible_engines": [],
                "list_price": round(random.uniform(89.99, 249.99), 2) if "Paint" in paint_type else round(random.uniform(29.99, 89.99), 2),
                "unit": "gallon" if "Paint" in paint_type or "Primer" in paint_type else "kit"
            })
            part_counter += 1
    
    # Zincs and anodes (25 items)
    zinc_types = [
        ("Hull Zinc", 8.99, 32.99),
        ("Prop Zinc", 12.99, 45.99),
        ("Shaft Zinc", 9.99, 38.99),
        ("Trim Tab Zinc", 14.99, 42.99),
        ("Engine Zinc", 6.99, 24.99),
    ]
    for zinc_name, price_min, price_max in zinc_types:
        for engine in ENGINE_CONFIGS[:4]:  # Only major brands
            parts.append({
                "part_number": f"ZNC-{part_counter}",
                "description": f"{engine['make']} {zinc_name}",
                "category": "Zincs/Anodes",
                "compatible_engines": [engine["make"]],
                "list_price": round(random.uniform(price_min, price_max), 2),
                "unit": "each"
            })
            part_counter += 1
    
    # Gaskets and seals (35 items)
    gasket_types = [
        "Exhaust Manifold Gasket",
        "Water Pump Gasket Kit",
        "Lower Unit Seal Kit",
        "Thermostat Gasket",
        "Valve Cover Gasket",
        "Drive Shaft Seal",
        "Trim Cylinder Seal Kit",
    ]
    for engine in ENGINE_CONFIGS:
        for gasket_type in gasket_types:
            if random.random() < 0.4:
                parts.append({
                    "part_number": f"GSK-{part_counter}",
                    "description": f"{engine['make']} {gasket_type}",
                    "category": "Gaskets/Seals",
                    "compatible_engines": [engine["make"]],
                    "list_price": round(random.uniform(12.99, 145.99), 2),
                    "unit": "kit" if "Kit" in gasket_type else "each"
                })
                part_counter += 1
    
    # Props and hardware (40 items)
    prop_sizes = ["13 1/4 x 17", "14 x 19", "14 1/2 x 21", "15 x 17", "15 1/2 x 19", "16 x 19"]
    prop_types = ["Aluminum", "Stainless Steel"]
    for engine in ENGINE_CONFIGS[:4]:
        for prop_type in prop_types:
            for size in random.sample(prop_sizes, 2):
                parts.append({
                    "part_number": f"PRP-{part_counter}",
                    "description": f"{engine['make']} {prop_type} Prop {size}",
                    "category": "Props & Hardware",
                    "compatible_engines": [engine["make"]],
                    "list_price": round(random.uniform(149.99, 549.99) if prop_type == "Stainless Steel" else random.uniform(89.99, 199.99), 2),
                    "unit": "each"
                })
                part_counter += 1
    
    # Prop hardware
    hardware_items = [
        ("Prop Nut Kit", 24.99, 49.99),
        ("Prop Washer Kit", 12.99, 29.99),
        ("Cotter Pin Set", 4.99, 12.99),
        ("Thrust Hub Kit", 39.99, 89.99),
        ("Prop Shaft Hardware Kit", 29.99, 69.99),
    ]
    for item_name, price_min, price_max in hardware_items:
        for engine in ENGINE_CONFIGS[:3]:
            parts.append({
                "part_number": f"HRD-{part_counter}",
                "description": f"{engine['make']} {item_name}",
                "category": "Props & Hardware",
                "compatible_engines": [engine["make"]],
                "list_price": round(random.uniform(price_min, price_max), 2),
                "unit": "kit"
            })
            part_counter += 1
    
    # Winterization and seasonal items (15 items)
    seasonal_items = [
        ("Marine Antifreeze (-50F)", 9.99, 14.99, "gallon"),
        ("Fuel Stabilizer", 12.99, 24.99, "bottle"),
        ("Fogging Oil", 8.99, 16.99, "can"),
        ("Shrink Wrap Kit", 149.99, 299.99, "kit"),
        ("Battery Tender", 29.99, 79.99, "each"),
        ("Engine Cover", 49.99, 149.99, "each"),
    ]
    for item_name, price_min, price_max, unit in seasonal_items:
        parts.append({
            "part_number": f"SEA-{part_counter}",
            "description": item_name,
            "category": "Seasonal",
            "compatible_engines": [],
            "list_price": round(random.uniform(price_min, price_max), 2),
            "unit": unit
        })
        part_counter += 1
        # Add brand variations
        for brand in ["Star Brite", "West Marine"]:
            if "Wrap" not in item_name and "Cover" not in item_name:
                parts.append({
                    "part_number": f"SEA-{part_counter}",
                    "description": f"{brand} {item_name}",
                    "category": "Seasonal",
                    "compatible_engines": [],
                    "list_price": round(random.uniform(price_min, price_max), 2),
                    "unit": unit
                })
                part_counter += 1
    
    # Miscellaneous supplies (remaining to reach ~300)
    misc_items = [
        ("Marine Grease Gun", 24.99, 49.99, "each"),
        ("Propeller Wrench Set", 19.99, 44.99, "set"),
        ("Drain Plug Kit", 8.99, 18.99, "kit"),
        ("Oil Drain Pump", 24.99, 49.99, "each"),
        ("Fuel Line Kit", 29.99, 59.99, "kit"),
        ("Throttle Cable", 49.99, 129.99, "each"),
        ("Shift Cable", 49.99, 129.99, "each"),
        ("Steering Cable", 89.99, 199.99, "each"),
        ("Control Box Rebuild Kit", 89.99, 189.99, "kit"),
        ("Primer Bulb Assembly", 12.99, 29.99, "each"),
        ("Fuel Tank Pickup", 18.99, 39.99, "each"),
        ("Fuel Connector Kit", 14.99, 34.99, "kit"),
        ("Water Separator Bowl", 19.99, 44.99, "each"),
        ("Marine Sealant 3M 5200", 14.99, 24.99, "tube"),
        ("Marine Sealant 3M 4200", 12.99, 22.99, "tube"),
    ]
    for item_name, price_min, price_max, unit in misc_items:
        parts.append({
            "part_number": f"MSC-{part_counter}",
            "description": item_name,
            "category": "Miscellaneous",
            "compatible_engines": [],
            "list_price": round(random.uniform(price_min, price_max), 2),
            "unit": unit
        })
        part_counter += 1
    
    return parts[:300]  # Ensure exactly 300 parts


# ============================================================================
# Work Order Generation
# ============================================================================

def generate_loa_range(loa: float) -> str:
    """Convert LOA to range bucket"""
    if loa < 20:
        return "15-20"
    elif loa < 25:
        return "20-25"
    elif loa < 30:
        return "25-30"
    elif loa < 35:
        return "30-35"
    elif loa < 40:
        return "35-40"
    else:
        return "40+"


def generate_work_orders(parts_catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate 100 historical work orders"""
    work_orders = []
    
    # Generate dates spanning the last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    for i in range(100):
        # Random vessel
        vessel_type_data = random.choice(VESSEL_TYPES)
        vessel_type = vessel_type_data["type"]
        loa = round(random.uniform(vessel_type_data["loa_min"], vessel_type_data["loa_max"]), 1)
        year = random.randint(2005, 2023)
        
        # Random engine
        engine_config = random.choice(ENGINE_CONFIGS)
        engine_make = engine_config["make"]
        engine_model = random.choice(engine_config["models"])
        
        # Random service
        service_cat_data = random.choice(SERVICE_CATEGORIES)
        service_category = service_cat_data["category"]
        service_data = random.choice(service_cat_data["services"])
        service_description = service_data["desc"]
        
        # Calculate labor
        hours_min, hours_max = service_data["hours_range"]
        # Adjust hours based on vessel size
        size_factor = 1.0 + (loa - 25) * 0.02  # Larger boats take more time
        base_hours = random.uniform(hours_min, hours_max)
        total_hours = round(base_hours * size_factor, 1)
        
        labor_rate = random.choice([115.00, 125.00, 135.00, 145.00])
        
        # Build labor items
        labor_items = []
        if total_hours <= 2:
            labor_items.append({
                "task": service_description,
                "hours": total_hours,
                "rate": labor_rate
            })
        else:
            # Split into multiple tasks
            remaining_hours = total_hours
            task_num = 1
            while remaining_hours > 0:
                task_hours = min(random.uniform(1.0, 2.5), remaining_hours)
                task_hours = round(task_hours, 1)
                labor_items.append({
                    "task": f"{service_description} - Phase {task_num}" if task_num > 1 else service_description,
                    "hours": task_hours,
                    "rate": labor_rate
                })
                remaining_hours -= task_hours
                task_num += 1
        
        # Build parts list
        parts_used = []
        total_parts_cost = 0.0
        
        # Find compatible parts from catalog
        compatible_parts = [p for p in parts_catalog if 
                           engine_make in p.get("compatible_engines", []) or 
                           len(p.get("compatible_engines", [])) == 0]
        
        # Add parts based on service type
        num_parts = random.randint(1, 4) if service_data["parts"] else 0
        if num_parts > 0 and compatible_parts:
            selected_parts = random.sample(compatible_parts, min(num_parts, len(compatible_parts)))
            for part in selected_parts:
                quantity = random.randint(1, 3) if part["unit"] in ["each", "quart"] else round(random.uniform(0.5, 2.0), 1)
                part_total = part["list_price"] * quantity
                parts_used.append({
                    "part_number": part["part_number"],
                    "description": part["description"],
                    "quantity": quantity,
                    "unit_price": part["list_price"]
                })
                total_parts_cost += part_total
        
        total_parts_cost = round(total_parts_cost, 2)
        total_labor = round(sum(item["hours"] * item["rate"] for item in labor_items), 2)
        total_invoice = round(total_labor + total_parts_cost, 2)
        
        # Random date
        random_days = random.randint(0, 730)
        completion_date = start_date + timedelta(days=random_days)
        
        # Determine season
        month = completion_date.month
        if month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        elif month in [9, 10, 11]:
            season = "fall"
        else:
            season = "winter"
        
        work_order = {
            "work_order_id": f"WO-{completion_date.year}-{str(i+1).zfill(4)}",
            "vessel_type": vessel_type,
            "loa": loa,
            "loa_range": generate_loa_range(loa),
            "year": year,
            "engine_make": engine_make,
            "engine_model": engine_model,
            "service_category": service_category,
            "service_description": service_description,
            "labor_items": labor_items,
            "parts_used": parts_used,
            "total_labor_hours": total_hours,
            "total_parts_cost": total_parts_cost,
            "total_invoice": total_invoice,
            "completion_date": completion_date.strftime("%Y-%m-%d"),
            "region": random.choice(REGIONS),
            "season": season
        }
        
        work_orders.append(work_order)
    
    return work_orders


# ============================================================================
# Labor Rates Generation
# ============================================================================

def generate_labor_rates() -> Dict[str, Any]:
    """Generate labor rates configuration"""
    return {
        "default_rate": 125.00,
        "rates_by_category": {
            "engine": 135.00,
            "hull": 115.00,
            "electrical": 125.00,
            "mechanical": 125.00,
            "outboard": 130.00,
            "inboard": 140.00,
            "annual": 125.00,
            "diagnostic": 145.00
        },
        "rates_by_region": {
            "Northeast": 1.10,
            "Southeast": 1.00,
            "Gulf Coast": 0.95,
            "Great Lakes": 1.00,
            "West Coast": 1.15,
            "Pacific Northwest": 1.10
        },
        "urgency_multipliers": {
            "routine": 1.0,
            "priority": 1.25,
            "emergency": 1.5
        },
        "last_updated": datetime.now().isoformat()
    }


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("EstimateIQ Synthetic Data Generator")
    print("=" * 50)
    
    # Generate parts catalog
    print("\nGenerating parts catalog (300 items)...")
    parts_catalog = generate_parts_catalog()
    parts_file = DATA_DIR / "parts_catalog.json"
    with open(parts_file, "w") as f:
        json.dump(parts_catalog, f, indent=2)
    print(f"  Saved {len(parts_catalog)} parts to {parts_file}")
    
    # Generate work orders
    print("\nGenerating work orders (100 records)...")
    work_orders = generate_work_orders(parts_catalog)
    work_orders_file = DATA_DIR / "work_orders.json"
    with open(work_orders_file, "w") as f:
        json.dump(work_orders, f, indent=2)
    print(f"  Saved {len(work_orders)} work orders to {work_orders_file}")
    
    # Generate labor rates
    print("\nGenerating labor rates configuration...")
    labor_rates = generate_labor_rates()
    labor_rates_file = DATA_DIR / "labor_rates.json"
    with open(labor_rates_file, "w") as f:
        json.dump(labor_rates, f, indent=2)
    print(f"  Saved labor rates to {labor_rates_file}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Data Generation Complete!")
    print(f"\nFiles created in {DATA_DIR}:")
    print(f"  - parts_catalog.json ({len(parts_catalog)} items)")
    print(f"  - work_orders.json ({len(work_orders)} records)")
    print(f"  - labor_rates.json")
    
    # Statistics
    print("\nWork Order Statistics:")
    categories = {}
    for wo in work_orders:
        cat = wo["service_category"]
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} orders")
    
    total_revenue = sum(wo["total_invoice"] for wo in work_orders)
    avg_invoice = total_revenue / len(work_orders)
    print(f"\nTotal Revenue: ${total_revenue:,.2f}")
    print(f"Average Invoice: ${avg_invoice:,.2f}")


if __name__ == "__main__":
    main()
