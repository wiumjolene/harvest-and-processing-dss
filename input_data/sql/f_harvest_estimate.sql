SELECT 
    recordno, 
    CONCAT(fc, '-', pu, '-', va) as block_id, 
    va as va_id, 
    week as time_id, 
    kg AS kg_raw
FROM
    pt_admin1718.harvest_estimates_quickadj
    WHERE season > 2019;