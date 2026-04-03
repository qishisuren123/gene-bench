# Example 1: EOQ and reorder point calculation
import numpy as np
from scipy.stats import norm

# Product demand statistics
daily_demand_mean = 50  # units/day
daily_demand_std = 12
lead_time_mean = 7  # days
lead_time_std = 2
service_level = 0.95
ordering_cost = 50  # $ per order
unit_cost = 10  # $ per unit
holding_pct = 0.25

# EOQ
annual_demand = daily_demand_mean * 365
holding_cost = unit_cost * holding_pct
eoq = np.sqrt(2 * annual_demand * ordering_cost / holding_cost)
print(f"EOQ: {eoq:.0f} units")

# Demand during lead time
mean_dlt = daily_demand_mean * lead_time_mean
var_dlt = lead_time_mean * daily_demand_std**2 + daily_demand_mean**2 * lead_time_std**2
std_dlt = np.sqrt(var_dlt)

# Safety stock and reorder point
z = norm.ppf(service_level)
safety_stock = z * std_dlt
reorder_point = mean_dlt + safety_stock
print(f"Safety stock: {safety_stock:.0f}, ROP: {reorder_point:.0f}")

# Example 2: Total annual cost
tc = (annual_demand / eoq) * ordering_cost + (eoq / 2) * holding_cost
print(f"Total annual cost: ${tc:.2f}")
