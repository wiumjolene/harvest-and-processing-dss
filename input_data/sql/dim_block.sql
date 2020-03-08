SELECT 
    pu.recordno AS id,
    pu.no AS name,
    pu.descr AS long_name,
    fc.recordno AS fc_id
FROM
    pt_admin1718.pu pu
        LEFT JOIN
    pt_admin1718.fc ON pu.fc = fc.no;