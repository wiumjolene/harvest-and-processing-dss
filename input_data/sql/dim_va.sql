SELECT 
    va.recordno AS id,
    va.no AS name,
    va.descr AS long_name,
    vg.recordno AS vacat_id
FROM
    pt_admin1718.va
    LEFT JOIN vg ON va.vagrp = vg.code
WHERE
    va.co = 'GR';
