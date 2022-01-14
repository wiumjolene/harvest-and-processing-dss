/*
RUN THIS PART FORM VITRAX CENTRAL,import data into dss.history_from_to
SELECT distinct grower, packsite FROM vview_0091_demand_union_planned_for_grapes
WHERE recordtype in ('PLANNED', '_PACKED');
*/

SELECT f_from_to.id, dim_packhouse.name as site, dim_fc.name as grower, dim_block.name as block, dim_fc.long_name as grower,
 f_from_to.allowed, f_from_to.history, f_from_to.km, historic.yes
FROM dss.f_from_to
LEFT JOIN dim_packhouse ON (dim_packhouse.id=f_from_to.packhouse_id)
LEFT JOIN dim_block ON (dim_block.id=f_from_to.block_id)
LEFT JOIN dim_fc ON (dim_fc.id=dim_block.fc_id)
LEFT JOIN (SELECT *, 1 as 'yes' FROM dss.history_from_to) historic 
ON (historic.grower=dim_fc.name AND historic.packsite=dim_packhouse.name)
WHERE (block_id = 45)
ORDER BY km;

/*
UPDATE `dss`.`f_from_to` 
LEFT JOIN dim_packhouse ON (dim_packhouse.id=f_from_to.packhouse_id)
LEFT JOIN dim_block ON (dim_block.id=f_from_to.block_id)
LEFT JOIN dim_fc ON (dim_fc.id=dim_block.fc_id)
LEFT JOIN (SELECT *, 1 as 'yes' FROM dss.history_from_to) historic 
	ON (historic.grower=dim_fc.name AND historic.packsite=dim_packhouse.name)
SET `history` = '1' 
WHERE (historic.yes = 1) and (block_id = 45); -- */

/*
UPDATE `dss`.`f_from_to` SET `allowed` = '0' 
where history=0 and allowed=2; -- */