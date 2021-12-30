SELECT f_from_to.* , dim_packhouse.province as siteP, dim_fc.province as fcP
FROM dss.f_from_to
LEFT JOIN dss.dim_packhouse ON (f_from_to.packhouse_id = dim_packhouse.id)
LEFT JOIN dss.dim_block ON (f_from_to.block_id = dim_block.id)
LEFT JOIN dss.dim_fc ON (dim_block.fc_id = dim_fc.id)
WHERE (dim_fc.province = "WC" and dim_packhouse.province = "NB");

-- UPDATE `dss`.`f_from_to`  
LEFT JOIN dss.dim_packhouse ON (f_from_to.packhouse_id = dim_packhouse.id)
LEFT JOIN dss.dim_block ON (f_from_to.block_id = dim_block.id)
LEFT JOIN dss.dim_fc ON (dim_block.fc_id = dim_fc.id)
SET `allowed` = 0
WHERE (dim_fc.province = "WC" and dim_packhouse.province = "NB");