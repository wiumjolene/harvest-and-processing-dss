SELECT 
    pc.recordno AS id,
    s.recordno as packhouse_id,
    CASE WHEN pc.packformat = 'PUNNET' THEN 1 ELSE 2 END as pack_type_id,
    pc.packweek,
    (pc.noofstdcartons * 4.5 * 1.2) AS kg,
    pc.noofstdcartons as stdunits
FROM
    pt_admin1718.packingcapacity pc
    LEFT JOIN sites s ON pc.phc = s.no;