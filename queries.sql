-- ==========================================================
-- Cybersecurity Incident Analytics
-- Business SQL Queries
-- Author: Pramod Prakash Jadhav
-- ==========================================================

-- ==========================================================
-- 1. Total Incidents
-- ==========================================================

SELECT COUNT(*) AS total_incidents
FROM cybersecurity_incidents;


-- ==========================================================
-- 2. Average Severity Score
-- ==========================================================

SELECT ROUND(AVG(severity_score), 2) AS average_severity
FROM cybersecurity_incidents;


-- ==========================================================
-- 3. Top 10 Most Severe Incidents
-- ==========================================================

SELECT
    incident_id,
    severity_score,
    attack_type,
    sector
FROM cybersecurity_incidents
ORDER BY severity_score DESC
LIMIT 10;


-- ==========================================================
-- 4. Incidents by Sector
-- ==========================================================

SELECT
    sector,
    COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY total_incidents DESC;


-- ==========================================================
-- 5. Incidents by Region
-- ==========================================================

SELECT
    region,
    COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY region
ORDER BY total_incidents DESC;


-- ==========================================================
-- 6. Attack Type Distribution
-- ==========================================================

SELECT
    attack_type,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY attack_type
ORDER BY incidents DESC;


-- ==========================================================
-- 7. Threat Actor Distribution
-- ==========================================================

SELECT
    threat_actor,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY threat_actor
ORDER BY incidents DESC;


-- ==========================================================
-- 8. Monthly Incident Trend
-- ==========================================================

SELECT
    incident_year,
    incident_month,
    COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY
    incident_year,
    incident_month
ORDER BY
    incident_year,
    incident_month;


-- ==========================================================
-- 9. Average Downtime by Sector
-- ==========================================================

SELECT
    sector,
    ROUND(
        AVG(downtime_hours),
        2
    ) AS avg_downtime
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY avg_downtime DESC;


-- ==========================================================
-- 10. Highest Financial Impact
-- ==========================================================

SELECT
    incident_id,
    total_financial_impact
FROM cybersecurity_incidents
ORDER BY total_financial_impact DESC
LIMIT 10;


-- ==========================================================
-- 11. Top Risk Score Incidents
-- ==========================================================

SELECT
    incident_id,
    risk_score,
    attack_type
FROM cybersecurity_incidents
ORDER BY risk_score DESC
LIMIT 10;


-- ==========================================================
-- 12. Zero-Day Attack Analysis
-- ==========================================================

SELECT
    zero_day_used,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY zero_day_used;


-- ==========================================================
-- 13. Data Exfiltration Analysis
-- ==========================================================

SELECT
    data_exfiltration,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY data_exfiltration;


-- ==========================================================
-- 14. Average Detection Time
-- ==========================================================

SELECT
    ROUND(
        AVG(detection_time_hours),
        2
    ) AS average_detection_time
FROM cybersecurity_incidents;


-- ==========================================================
-- 15. Average Response Team Size
-- ==========================================================

SELECT
    ROUND(
        AVG(response_team_size),
        2
    ) AS average_team_size
FROM cybersecurity_incidents;


-- ==========================================================
-- 16. Resolution Success Rate
-- ==========================================================

SELECT
    ROUND(
        AVG(resolved_within_7_days) * 100,
        2
    ) AS success_rate
FROM cybersecurity_incidents;


-- ==========================================================
-- 17. Average Records Affected by Attack Type
-- ==========================================================

SELECT
    attack_type,
    ROUND(
        AVG(records_affected),
        2
    ) AS average_records
FROM cybersecurity_incidents
GROUP BY attack_type
ORDER BY average_records DESC;


-- ==========================================================
-- 18. High Severity Incidents
-- ==========================================================

SELECT
    incident_id,
    severity_score,
    sector
FROM cybersecurity_incidents
WHERE severity_score >= 8
ORDER BY severity_score DESC;


-- ==========================================================
-- 19. Weekend Incident Analysis
-- ==========================================================

SELECT
    is_weekend,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY is_weekend;


-- ==========================================================
-- 20. Top 5 Sectors by Financial Loss
-- ==========================================================

SELECT
    sector,
    ROUND(
        SUM(total_financial_impact),
        2
    ) AS total_loss
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY total_loss DESC
LIMIT 5;


-- ==========================================================
-- 21. Average Risk Score by Sector
-- ==========================================================

SELECT
    sector,
    ROUND(
        AVG(risk_score),
        2
    ) AS avg_risk
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY avg_risk DESC;


-- ==========================================================
-- 22. Most Common Threat Actor per Region
-- ==========================================================

SELECT
    region,
    threat_actor,
    COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY
    region,
    threat_actor
ORDER BY incidents DESC;


-- ==========================================================
-- 23. Top 10 Longest Downtime Incidents
-- ==========================================================

SELECT
    incident_id,
    downtime_hours,
    attack_type
FROM cybersecurity_incidents
ORDER BY downtime_hours DESC
LIMIT 10;


-- ==========================================================
-- 24. Incident Complexity Analysis
-- ==========================================================

SELECT
    incident_id,
    incident_complexity_score
FROM cybersecurity_incidents
ORDER BY incident_complexity_score DESC
LIMIT 10;


-- ==========================================================
-- 25. Dashboard KPI Query
-- ==========================================================

SELECT

    COUNT(*) AS total_incidents,

    ROUND(
        AVG(severity_score),
        2
    ) AS avg_severity,

    ROUND(
        AVG(downtime_hours),
        2
    ) AS avg_downtime,

    ROUND(
        SUM(total_financial_impact),
        2
    ) AS total_financial_loss,

    ROUND(
        AVG(risk_score),
        2
    ) AS average_risk_score

FROM cybersecurity_incidents;
