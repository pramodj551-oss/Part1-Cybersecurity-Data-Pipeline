-- ==========================================================
-- Cybersecurity Incident Analytics
-- Production SQL Analytics Queries
-- Author: Pramod Prakash Jadhav
-- ==========================================================
-- SQLite-compatible queries for cybersecurity_incidents.
-- ==========================================================

-- 1. Total Incidents
SELECT COUNT(*) AS total_incidents
FROM cybersecurity_incidents;

-- 2. Average Severity Score
SELECT ROUND(AVG(severity_score), 2) AS average_severity
FROM cybersecurity_incidents;

-- 3. Top 10 Most Severe Incidents
SELECT incident_id, severity_score, attack_type, sector
FROM cybersecurity_incidents
ORDER BY severity_score DESC, incident_id
LIMIT 10;

-- 4. Incidents by Sector
SELECT sector, COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY total_incidents DESC, sector;

-- 5. Incidents by Region
SELECT region, COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY region
ORDER BY total_incidents DESC, region;

-- 6. Attack Type Distribution
SELECT attack_type, COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY attack_type
ORDER BY incidents DESC, attack_type;

-- 7. Threat Actor Distribution
SELECT threat_actor, COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY threat_actor
ORDER BY incidents DESC, threat_actor;

-- 8. Monthly Incident Trend
SELECT incident_year, incident_month, COUNT(*) AS total_incidents
FROM cybersecurity_incidents
GROUP BY incident_year, incident_month
ORDER BY incident_year, incident_month;

-- 9. Average Downtime by Sector
SELECT sector, ROUND(AVG(downtime_hours), 2) AS avg_downtime
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY avg_downtime DESC, sector;

-- 10. Highest Financial Impact
SELECT incident_id, total_financial_impact
FROM cybersecurity_incidents
ORDER BY total_financial_impact DESC, incident_id
LIMIT 10;

-- 11. Top Risk Score Incidents
SELECT incident_id, risk_score, attack_type
FROM cybersecurity_incidents
ORDER BY risk_score DESC, incident_id
LIMIT 10;

-- 12. Zero-Day Attack Analysis
SELECT zero_day_used, COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY zero_day_used
ORDER BY zero_day_used DESC;

-- 13. Data Exfiltration Analysis
SELECT data_exfiltration, COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY data_exfiltration
ORDER BY data_exfiltration DESC;

-- 14. Average Detection Time
SELECT ROUND(AVG(detection_time_hours), 2) AS average_detection_time
FROM cybersecurity_incidents;

-- 15. Average Response Team Size
SELECT ROUND(AVG(response_team_size), 2) AS average_team_size
FROM cybersecurity_incidents;

-- 16. Resolution Success Rate
SELECT ROUND(AVG(CAST(resolved_within_7_days AS REAL)) * 100, 2) AS success_rate
FROM cybersecurity_incidents;

-- 17. Average Records Affected by Attack Type
SELECT attack_type, ROUND(AVG(records_affected), 2) AS average_records
FROM cybersecurity_incidents
GROUP BY attack_type
ORDER BY average_records DESC, attack_type;

-- 18. High Severity Incidents
SELECT incident_id, severity_score, sector
FROM cybersecurity_incidents
WHERE severity_score >= 8
ORDER BY severity_score DESC, incident_id;

-- 19. Weekend Incident Analysis
SELECT is_weekend, COUNT(*) AS incidents
FROM cybersecurity_incidents
GROUP BY is_weekend
ORDER BY is_weekend DESC;

-- 20. Top 5 Sectors by Financial Loss
SELECT sector, ROUND(SUM(total_financial_impact), 2) AS total_loss
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY total_loss DESC, sector
LIMIT 5;

-- 21. Average Risk Score by Sector
SELECT sector, ROUND(AVG(risk_score), 2) AS avg_risk
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY avg_risk DESC, sector;

-- 22. Most Common Threat Actor per Region
-- Uses a window function so only the top actor(s) per region are returned.
WITH actor_counts AS (
    SELECT
        region,
        threat_actor,
        COUNT(*) AS incidents
    FROM cybersecurity_incidents
    GROUP BY region, threat_actor
), ranked AS (
    SELECT
        region,
        threat_actor,
        incidents,
        RANK() OVER (
            PARTITION BY region
            ORDER BY incidents DESC
        ) AS actor_rank
    FROM actor_counts
)
SELECT region, threat_actor, incidents
FROM ranked
WHERE actor_rank = 1
ORDER BY region, threat_actor;

-- 23. Top 10 Longest Downtime Incidents
SELECT incident_id, downtime_hours, attack_type
FROM cybersecurity_incidents
ORDER BY downtime_hours DESC, incident_id
LIMIT 10;

-- 24. Top 10 Most Complex Incidents
SELECT incident_id, incident_complexity_score
FROM cybersecurity_incidents
ORDER BY incident_complexity_score DESC, incident_id
LIMIT 10;

-- 25. Dashboard KPI Query
SELECT
    COUNT(*) AS total_incidents,
    ROUND(AVG(severity_score), 2) AS avg_severity,
    ROUND(AVG(downtime_hours), 2) AS avg_downtime,
    ROUND(SUM(total_financial_impact), 2) AS total_financial_loss,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    ROUND(AVG(CAST(resolved_within_7_days AS REAL)) * 100, 2) AS resolution_success_rate,
    ROUND(AVG(detection_time_hours), 2) AS avg_detection_time
FROM cybersecurity_incidents;

-- ==========================================================
-- 26. High-Risk Incident Count
-- ==========================================================
SELECT COUNT(*) AS high_risk_incidents
FROM cybersecurity_incidents
WHERE risk_score >= 20;

-- ==========================================================
-- 27. Financial Impact by Attack Type
-- ==========================================================
SELECT
    attack_type,
    COUNT(*) AS incidents,
    ROUND(SUM(total_financial_impact), 2) AS total_financial_impact,
    ROUND(AVG(total_financial_impact), 2) AS avg_financial_impact
FROM cybersecurity_incidents
GROUP BY attack_type
ORDER BY total_financial_impact DESC, attack_type;

-- ==========================================================
-- 28. Resolution Performance by Sector
-- ==========================================================
SELECT
    sector,
    COUNT(*) AS incidents,
    ROUND(AVG(CAST(resolved_within_7_days AS REAL)) * 100, 2) AS resolution_rate
FROM cybersecurity_incidents
GROUP BY sector
ORDER BY resolution_rate DESC, sector;

-- ==========================================================
-- 29. Data Quality Sanity Check
-- ==========================================================
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT incident_id) AS distinct_incident_ids,
    SUM(CASE WHEN incident_id IS NULL THEN 1 ELSE 0 END) AS null_incident_ids,
    SUM(CASE WHEN severity_score IS NULL THEN 1 ELSE 0 END) AS null_severity_scores,
    SUM(CASE WHEN incident_date IS NULL THEN 1 ELSE 0 END) AS null_incident_dates
FROM cybersecurity_incidents;
