SELECT 
    demandid AS id,
    targetmarket AS client_id,
    varietygroup AS vacat_id,
    cartontype AS pack_type_id,
    priority,
    demand_arrivalweek as time_id,
    qty_standardctns AS stdunits
FROM
    pt_admin1718.vview_0091_demand_union_planned_for_grapes
WHERE
    recordtype = 'DEMAND'
    AND demand_arrivalweek > '20-08'
    AND commodity = 'GR';
    
    