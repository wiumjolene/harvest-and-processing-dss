SELECT 
	d.demandid as id,
	tk.recordno as client_id,
	vg.recordno as vacat_id,
	IF((SUBSTR(d.cartontype, 1, 1) = 'A'),
		IF((d.cartontype = 'A75F'),
			2, -- LOOSE
			1), -- PUNNET
		2) AS 'pack_type_id',
	-- d.priority,
    CASE WHEN d.priority = '-' THEN 0 ELSE d.priority END as priority,
	d.demand_arrivalweek as arrivalweek,
    cd.transitdays,
	ROUND(d.qty_standardctns,2) AS stdunits
FROM
    pt_admin1718.vview_0091_demand_union_planned_for_grapes d
    LEFT JOIN pt_admin1718.tk ON d.targetmarket = tk.no
    LEFT JOIN pt_admin1718.vg ON d.varietygroup = vg.code
    LEFT JOIN pt_admin1718.clientdemands cd ON d.demandid = cd.recordno
WHERE
    d.recordtype = 'DEMAND'
    AND d.demand_arrivalweek > '19-30'
    AND d.commodity = 'GR'
    AND tk.no <> 'AF';
    
    
    
 