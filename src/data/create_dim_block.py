-- INSERT INTO `dss`.`dim_block` (`name`, `fc_id`, `pu_id`, `va_id`, `hectare`)  
SELECT distinct Orchard as name  
, dim_fc.id as fc_id  
-- , Grower
-- , ProductionUnit  
, pu.id as pu_id  
-- , Variety  
, dim_va.id as va_id  
, Hectare as hectare  
FROM dss.harvest_estimate_data d  
LEFT JOIN dim_fc ON (dim_fc.name = d.Grower)  
LEFT JOIN dim_productionunit pu ON (dim_fc.id=pu.fc_id AND d.ProductionUnit=pu.name)  
LEFT JOIN dim_va ON (dim_va.name = d.Variety)  
WHERE estimatetype='BUDGET2' AND Season=2022
