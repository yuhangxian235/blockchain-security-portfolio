-- 02_phishing_drain.sql
-- KYT dashboard metric #2 (R1+R2): candidate phishing drains.
-- Logic: an UNLIMITED approval (owner -> spender), then within 30 minutes an
-- ERC-20 Transfer moves the token OUT of the owner to a third party (not the
-- owner itself). That third-party transferFrom is the drain signature.
-- Output is a candidate list; an analyst confirms on Etherscan (like our case).

WITH approvals AS (
  SELECT contract_address,
         owner,
         spender,
         evt_block_time,
         evt_block_number
  FROM ethereum."ERC20_evt_Approval"
  WHERE evt_block_time >= now() - interval '30' day
    AND value = CAST('57896044618658097711785492504343953926634992332820282019728792003956564819935' AS DECIMAL(78,0))
),
drains AS (
  SELECT contract_address,
         "from" AS victim,
         "to"   AS receiver,
         value,
         evt_block_time,
         evt_block_number
  FROM ethereum."ERC20_evt_Transfer"
  WHERE evt_block_time >= now() - interval '30' day
    AND "from" <> "to"
)
SELECT a.evt_block_time            AS approve_time,
       d.evt_block_time            AS drain_time,
       date_diff('second', a.evt_block_time, d.evt_block_time) AS seconds_after,
       a.owner                     AS victim,
       a.spender                   AS malicious_spender,
       d.receiver                  AS hub,
       d.value
FROM approvals a
JOIN drains d
  ON d.contract_address = a.contract_address
 AND d.victim = a.owner
 AND d.evt_block_time > a.evt_block_time
 AND d.evt_block_time <= a.evt_block_time + interval '30' minute
WHERE a.owner <> a.spender
ORDER BY seconds_after ASC
LIMIT 500;
