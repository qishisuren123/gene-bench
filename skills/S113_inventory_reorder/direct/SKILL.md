# Inventory Reorder Point and EOQ Optimization

## Overview
This skill computes optimal inventory reorder points and Economic Order Quantities (EOQ) from historical demand data, incorporating safety stock calculations for target service levels.

## Workflow
1. Parse arguments for input CSV, output JSON, target service level (default 0.95), and holding cost percentage
2. Load historical demand data (date, product_id, demand_quantity, lead_time_days) and group by product
3. For each product: compute demand statistics (daily mean, std, CV) and lead time statistics (mean, std)
4. Calculate EOQ using Wilson formula: Q* = sqrt(2 * D * K / h) where D=annual demand, K=ordering cost, h=unit holding cost
5. Calculate demand during lead time: mean = daily_mean * lead_time_mean, std = sqrt(LT*Var(D) + D²*Var(LT))
6. Calculate safety stock = z * std_demand_during_lead_time where z = norm.ppf(service_level)
7. Calculate reorder point = mean_demand_during_lead_time + safety_stock
8. Compute total annual cost = (D/Q)*K + (Q/2)*h and output results per product

## Common Pitfalls
- **Lead time demand variance**: Must combine both demand variability AND lead time variability: Var_DLT = LT_mean * Var_D + D_mean² * Var_LT — using only Var_D underestimates safety stock
- **EOQ constant demand assumption**: EOQ formula assumes steady demand; for high CV (>0.5), the EOQ is unreliable — flag these products
- **Service level z-score**: Use scipy.stats.norm.ppf(service_level), NOT the confidence interval z-value; 0.95 service → z=1.645, not 1.96
- **Annual vs daily**: EOQ uses annual demand D but lead time is in days — ensure consistent units when computing demand during lead time
- **Zero demand products**: Products with zero demand in the historical data should be flagged, not crash the computation

## Error Handling
- Handle products with fewer than 2 demand observations (cannot compute std)
- Validate service_level is between 0 and 1
- Handle division by zero in CV calculation when mean demand is zero
- Cap safety stock at reasonable multiples of mean demand to prevent overflow

## Quick Reference
- EOQ: `Q = sqrt(2 * annual_demand * ordering_cost / holding_cost_per_unit)`
- Safety stock: `SS = norm.ppf(service_level) * sqrt(LT_mean * demand_var + demand_mean**2 * LT_var)`
- Reorder point: `ROP = demand_mean * LT_mean + SS`
- Total cost: `TC = (D/Q) * K + (Q/2) * h`
- Holding cost per unit: `h = unit_cost * holding_cost_pct`
