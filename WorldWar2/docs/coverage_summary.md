# Coverage summary (2 November 2026)

> **Historical snapshot (2 November 2026).** This page is a hand-written summary of coverage as of that date (7,055 claims, 319 units with claims). It is not live coverage and should not be used for current headline figures. For current counts see the generated [coverage.md](coverage.md).

Read from `build/coverage_by_unit.csv`, `build/coverage_by_month.csv` and `build/review_queue.csv` as built on 2 November 2026 (7,055 claims, 319 units with claims). Method: [coverage_report.md](coverage_report.md). This page is written by hand; the tables are regenerated on every build, so the figures here date.

## Top findings

1. **The situation maps carry most of the dataset.** About two thirds of all rows are map-only: US 72%, UK 70%, Germany 65%, France 64%, Canada 56%, Poland 47%.
2. **German units are the weakest.** 35 of the top 50 queue places are German; 29 German units have a gap of 60 days or more; their rows are mostly at confidence 0.3 (map readings of an intelligence picture).
3. **German monthly coverage drops in October 1944 and January to March 1945.** In February 1945, 67 of 88 active German units have a claim (21 without); in January 1945, 91 of 105; the map-only share in those months is 79-85%.
4. **Long Allied gaps probably sit where the 12th Army Group maps do not reach** (to be checked): XVIII Airborne Corps 25 Aug to 19 Dec 1944 (First Allied Airborne Army, Market Garden), the 94th Infantry Division 10 Sep 1944 to 1 Jan 1945 (Brittany ports). The CMH volumes for those operations are the obvious next read.
5. **Single-family units:** 25 units have all rows from one source family (14 German); 20 units have a single claim, which the score cannot rank well.

## Top 10 of the review queue

| rank | unit | read | score | why |
|---|---|---|---:|---|
| 1 | `GER-COR-086C` LXXXVI Corps | 1944-07-18 to 1944-10-17 | 0.6576 | gap of 91 days (1944-07-18 to 1944-10-17); 79% of rows from situation maps only; 86% of rows at confidence 0.3 or less; 2 month(s) with no claim |
| 2 | `GER-INF-226D` 226th Infantry Division | 1944-09-05 to 1944-12-15 | 0.65 | gap of 101 days (1944-09-05 to 1944-12-15); 50% of rows from situation maps only; 100% of rows at confidence 0.3 or less; 2 month(s) with no claim |
| 3 | `GER-SSCOR-012C` XII SS Corps | 1945-01-23 to 1945-04-15 | 0.634 | gap of 82 days (1945-01-23 to 1945-04-15); 71% of rows from situation maps only; 93% of rows at confidence 0.3 or less; 2 month(s) with no claim |
| 4 | `GER-VG-047D` 47th Volksgrenadier Division | 1945-01-23 to 1945-04-09 | 0.6306 | gap of 76 days (1945-01-23 to 1945-04-09); 82% of rows from situation maps only; 82% of rows at confidence 0.3 or less; 2 month(s) with no claim |
| 5 | `GER-PZ-011D` 11th Panzer Division | 1944-06-06 to 1944-09-18 | 0.6099 | gap of 104 days (1944-06-06 to 1944-09-18); 66% of rows from situation maps only; 72% of rows at confidence 0.3 or less; 3 month(s) with no claim |
| 6 | `US-ABN-018C` XVIII Airborne Corps | 1944-08-25 to 1944-12-19 | 0.6063 | gap of 116 days (1944-08-25 to 1944-12-19); 79% of rows from situation maps only; 3 month(s) with no claim |
| 7 | `GER-INF-344D` 344th Infantry Division | 1944-09-05 to 1944-11-07 | 0.6036 | gap of 63 days (1944-09-05 to 1944-11-07); 91% of rows from situation maps only; 91% of rows at confidence 0.3 or less; 1 month(s) with no claim |
| 8 | `GER-PZ-116D` 116th Panzer Division | 1944-12-20 to 1945-03-26 | 0.5982 | gap of 96 days (1944-12-20 to 1945-03-26); 63% of rows from situation maps only; 73% of rows at confidence 0.3 or less; 2 month(s) with no claim |
| 9 | `GER-SSCOR-013C` XIII SS Corps | 1944-12-03 to 1945-04-02 | 0.5768 | gap of 120 days (1944-12-03 to 1945-04-02); 54% of rows from situation maps only; 62% of rows at confidence 0.3 or less; 3 month(s) with no claim |
| 10 | `US-INF-094D` 94th Infantry Division | 1944-09-10 to 1945-01-01 | 0.574 | gap of 113 days (1944-09-10 to 1945-01-01); 68% of rows from situation maps only; 3 month(s) with no claim |

Suggested sources are in `build/review_queue.csv` (FMS manuscripts and Lexikon/Tessin for the German units; CMH Green Books for the US ones).
