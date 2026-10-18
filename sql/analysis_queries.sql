-- Sales totals are in millions of units.
-- If you chose a different database, change the USE statement below.
USE `gamepulse`;

-- 1. Total global sales by genre.
SELECT `Genre`, SUM(`Global_Sales`) AS total_global_sales
FROM `video_game_sales`
GROUP BY `Genre`
ORDER BY total_global_sales DESC, `Genre`;

-- 2. Total global sales by platform.
SELECT `Platform`, SUM(`Global_Sales`) AS total_global_sales
FROM `video_game_sales`
GROUP BY `Platform`
ORDER BY total_global_sales DESC, `Platform`;

-- 3. Top 10 publishers by global sales (including Unknown).
SELECT `Publisher`, SUM(`Global_Sales`) AS total_global_sales
FROM `video_game_sales`
GROUP BY `Publisher`
ORDER BY total_global_sales DESC, `Publisher`
LIMIT 10;

-- 4. Yearly global sales trend, ordered from earliest to latest year.
SELECT `Year`, SUM(`Global_Sales`) AS total_global_sales
FROM `video_game_sales`
GROUP BY `Year`
ORDER BY `Year`;

-- 5. Compare North American, European, and Japanese sales by genre.
SELECT `Genre`,
       SUM(`NA_Sales`) AS total_na_sales,
       SUM(`EU_Sales`) AS total_eu_sales,
       SUM(`JP_Sales`) AS total_jp_sales
FROM `video_game_sales`
GROUP BY `Genre`
ORDER BY `Genre`;
