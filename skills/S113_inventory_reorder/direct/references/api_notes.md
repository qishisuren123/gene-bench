# scipy.stats.norm.ppf
ppf(q) — percent point function (inverse CDF of standard normal)
- ppf(0.95) = 1.6449 (95% service level)
- ppf(0.99) = 2.3263 (99% service level)

# numpy.sqrt, numpy.mean, numpy.std
- std(ddof=1) for sample standard deviation
- Use ddof=1 for unbiased estimate from sample data

# EOQ (Wilson formula)
Q* = sqrt(2 * D * K / h)
- D: annual demand (units/year)
- K: fixed ordering cost per order ($)
- h: annual holding cost per unit ($/unit/year)
- h = unit_cost * holding_cost_percentage

# Demand during lead time statistics
mean_DLT = mean_daily_demand * mean_lead_time
var_DLT = mean_lead_time * var_daily_demand + mean_daily_demand**2 * var_lead_time
std_DLT = sqrt(var_DLT)
