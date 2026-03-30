Write a Python CLI script that computes optimal inventory reorder points and quantities using demand forecasting.

Input: A CSV file with columns: date, product_id, demand_quantity, lead_time_days (historical demand data).

Requirements:
1. Use argparse: --input CSV, --output JSON, --service-level (default 0.95), --holding-cost-pct (default 0.25 annually)
2. Load historical demand data grouped by product_id
3. For each product:
   - Compute demand statistics: mean, std, coefficient of variation
   - Fit demand distribution (normal or Poisson based on CV)
   - Compute average lead time and its variability
4. Calculate Economic Order Quantity (EOQ): Q* = sqrt(2*D*K / h)
   - D = annual demand, K = fixed ordering cost ($50), h = holding cost per unit
5. Calculate Reorder Point: ROP = mean_demand_during_lead_time + safety_stock
   - Safety stock = z * std_demand_during_lead_time (z from service level)
6. Compute expected total annual cost: ordering + holding + stockout cost
7. Output JSON per product: {product_id, eoq, reorder_point, safety_stock, service_level, annual_cost, demand_stats}
8. Print summary: products analyzed, total inventory investment, average service level
