SELECT 
    si.recordno AS id,
    s.phc AS name,
    si.descr AS long_name,
    CASE
        WHEN
            MAX(CASE
                WHEN s.packformat = 'LOOSE' THEN s.noofstdcartons
            END) > 0
                AND MAX(CASE
                WHEN s.packformat = 'PUNNET' THEN s.noofstdcartons
            END) > 0
        THEN
            3
        WHEN
            MAX(CASE
                WHEN s.packformat = 'LOOSE' THEN s.noofstdcartons
            END) IS NULL
                AND MAX(CASE
                WHEN s.packformat = 'PUNNET' THEN s.noofstdcartons
            END) > 0
        THEN
            1
        WHEN
            MAX(CASE
                WHEN s.packformat = 'LOOSE' THEN s.noofstdcartons
            END) > 0
                AND MAX(CASE
                WHEN s.packformat = 'PUNNET' THEN s.noofstdcartons
            END) IS NULL
        THEN
            2
        ELSE 4
    END AS type,
    MAX(CASE
        WHEN s.packformat = 'LOOSE' THEN s.noofstdcartons
    END) 'loose',
    MAX(CASE
        WHEN s.packformat = 'PUNNET' THEN s.noofstdcartons
    END) 'punnet'
FROM
    pt_admin1718.packingcapacity s
        LEFT JOIN
    pt_admin1718.sites si ON s.phc = si.no
    WHERE left(packweek,2) > 18
GROUP BY s.phc;