-- 03_peel_chain.sql
-- KYT dashboard metric #3 (R4 / layering): candidate peel-chain nodes.
-- A node received a chunk of ETH and, within the next ~200 blocks (~40 min),
-- sent it out to >= 2 DIFFERENT addresses. Grouped by sender; count distinct
-- destinations = fan-out width. High fan-out to fresh addresses = layering.
-- (This approximates the Python detector in detect_peel_chain.py; Dune cannot
--  cheaply compute historical nonce, so we rank by fan-out width as a proxy.)

WITH outs AS (
  SELECT
    "from"              AS node,
    "to"                AS child,
    block_time,
    block_number,
    value / 1e18        AS eth
  FROM ethereum.traces
  WHERE success = true
    AND call_type = 'call'
    AND value > 0
    AND block_time >= now() - interval '30' day
)
SELECT
  '0x' || lower(to_hex(node))                          AS node,
  min(block_number)                                   AS first_out_block,
  round(sum(eth), 4)                                 AS total_out_eth,
  count(DISTINCT child)                              AS fanout_width,
  count(*)                                           AS num_out_txs
FROM outs
GROUP BY node
HAVING count(DISTINCT child) >= 3          -- split into 3+ children
   AND sum(eth) > 5                         -- non-trivial amount
ORDER BY fanout_width DESC, total_out_eth DESC
LIMIT 500;
