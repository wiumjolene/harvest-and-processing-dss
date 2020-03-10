SELECT 
    qaj.recordno as id,
    pu.recordno AS block_id,
    va.recordno AS va_id,
    qaj.week AS packweek,
    qaj.kg AS kg_raw
FROM
    pt_admin1718.harvest_estimates_quickadj qaj 
    LEFT JOIN va ON qaj.va = va.no
    LEFT JOIN pu ON (qaj.pu = pu.no AND qaj.fc = pu.fc)
WHERE
    season > 2019;