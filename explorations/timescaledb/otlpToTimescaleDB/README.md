# Notes on setting up TimescaleDB to receive OTLP metrics

## TimescaleDB notes
### Metrics queries
#### Mimic Prometheus query
Can mimic the following Prometheus query in TimescaleDB:
```
avg_over_time(system_throughputPerformance_current{name =~ ".*ServerBitsIn|.*ServerBitsOut"}[1m])
```
with the TimescaleDB equivalent being:
```
SELECT
  $__timeGroupAlias("time",$__interval),
  avg(value) AS "metric",
  jsonb(labels) ->> 'name' as name
FROM "system_throughputPerformance_current"
WHERE
  $__timeFilter("time")
  and labels ? ('name' ==~ '.*ServerBitsIn|.*ServerBitsOut')
GROUP BY 1,name
ORDER BY 1,name
```
where the default $__interval value = 60 seconds


## Sources used
* [Promscale by TimescaleDB](https://github.com/timescale/promscale)
* [Promscale in Docker](https://github.com/timescale/promscale/blob/master/docs/docker.md)
* [How Promscale stores Prometheus metrics](https://github.com/timescale/promscale/blob/master/docs/sql_schema.md)