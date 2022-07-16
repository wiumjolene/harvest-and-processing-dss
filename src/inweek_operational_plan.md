# In Week Operational Plan: Changes

## 1. Add packaging to `f_demand_plan` for swop index.

`swop_index` to consist of: day_packhouse_cartontype_inner_brand

```
SELECT demandid, concat(cartontype, "-", innerpacking, "-", brand) as packaging
FROM dss.planning_data
WHERE recordtype='DEMAND'
AND extract_datetime = (SELECT MAX(extract_datetime) FROM dss.planning_data);
```


## 2. Make a new individual

### Plan for the week
```
SELECT sol_pareto_individuals.demand_id
	-- , sol_pareto_individuals.he 
	, sol_pareto_individuals.pc 
	, ROUND(SUM(sol_pareto_individuals.kg), 1) as kg
FROM dss.sol_pareto_individuals
LEFT JOIN sol_fitness ON (sol_pareto_individuals.indiv_id = sol_fitness.indiv_id 
	AND sol_pareto_individuals.alg = sol_fitness.alg 
    AND sol_pareto_individuals.plan_date = sol_fitness.plan_date
	AND sol_fitness.result = 'final result')
WHERE kg > 0
AND sol_pareto_individuals.plan_date = '2021-12-08'
AND sol_pareto_individuals.time_id = 1076
AND sol_fitness.id = 273
-- AND pc = 4722
GROUP BY sol_pareto_individuals.demand_id, sol_pareto_individuals.pc;
```

### Daily capacity per pc
```
SELECT f_pack_capacity.id as pc
-- , f_pack_capacity.packhouse_id
-- , f_pack_capacity.pack_type_id
-- , f_pack_capacity.stdunits
, dim_time.id as day_id
, IF(stdunits>0, ROUND((stdunits / dim_week.workdays)  * dim_time.workday), 0)  as stdunits_day
-- , dim_week.id as time_id
FROM dss.f_pack_capacity
LEFT JOIN dim_week on (dim_week.week = f_pack_capacity.packweek)
LEFT JOIN dim_time on (dim_time.week = f_pack_capacity.packweek)
WHERE f_pack_capacity.plan_date = '2021-12-08'
AND dim_time.workday > 0
AND dim_week.id = 1076
-- AND f_pack_capacity.id = 4722
ORDER BY packhouse_id, pack_type_id
;
```

## 3. Calculate fitness


# Gene structure
Gene = pc