SELECT f_from_to.* 
	, dim_packhouse.province as siteP
	, dim_fc.province as fcP
	, dim_fc.name as fc
    , dim_block.name as block
	, dim_packhouse.name as site
FROM dss.f_from_to
LEFT JOIN dss.dim_packhouse ON (f_from_to.packhouse_id = dim_packhouse.id)
LEFT JOIN dss.dim_block ON (f_from_to.block_id = dim_block.id)
LEFT JOIN dss.dim_fc ON (dim_block.fc_id = dim_fc.id)
WHERE 
dim_block.name = '523' and dim_packhouse.name = 'KBS'
-- dim_fc.province = 'NC' and dim_packhouse.province = 'LP'
-- and allowed <> 0
-- dim_fc.name in () 
-- and dim_packhouse.name = "HNP"
;

/*
UPDATE `dss`.`f_from_to`  
LEFT JOIN dss.dim_packhouse ON (f_from_to.packhouse_id = dim_packhouse.id)
LEFT JOIN dss.dim_block ON (f_from_to.block_id = dim_block.id)
LEFT JOIN dss.dim_fc ON (dim_block.fc_id = dim_fc.id)
SET `km` = 177.50, `f_from_to`.`add_datetime` = now()
WHERE 
dim_block.name = '523' and dim_packhouse.name = 'RFY'
;-- */