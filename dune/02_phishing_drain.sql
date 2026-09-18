-- 02_phishing_drain.sql  (v2: raw-logs version, most robust)
-- KYT dashboard metric #2 (R1+R2): candidate phishing drains.
-- Logic: an UNLIMITED approval (owner -> spender), then within 30 min an
-- ERC-20 Transfer moves tokens OUT of the owner to a third party.
-- We read RAW logs (ethereum.logs) and decode the topics ourselves:
--   Approval: topic0=0x8c5be1e5..., topic1=owner, topic2=spender, data=allowance
--   Transfer: topic0=0xddf252ad..., topic1=from,  topic2=to
-- Addresses are the last 20 bytes (bytes 13..32) of each 32-byte topic.

WITH approvals AS (
  SELECT
    contract_address,
    bytearray_substring(topic1, 13, 20) AS owner,
    bytearray_substring(topic2, 13, 20) AS spender,
    block_time
  FROM ethereum.logs
  WHERE topic0 = 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925
    AND data = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    AND block_time >= now() - interval '30' day
),
drains AS (
  SELECT
    contract_address,
    bytearray_substring(topic1, 13, 20) AS victim,
    bytearray_substring(topic2, 13, 20) AS receiver,
    block_time
  FROM ethereum.logs
  WHERE topic0 = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
    AND block_time >= now() - interval '30' day
)
SELECT
  a.block_time                                               AS approve_time,
  d.block_time                                               AS drain_time,
  date_diff('second', a.block_time, d.block_time)             AS seconds_after,
  '0x' || lower(to_hex(a.owner))                             AS victim,
  '0x' || lower(to_hex(a.spender))                          AS malicious_spender,
  '0x' || lower(to_hex(d.receiver))                         AS hub
FROM approvals a
JOIN drains d
  ON d.contract_address = a.contract_address
 AND d.victim = a.owner
 AND d.block_time > a.block_time
 AND d.block_time <= a.block_time + interval '30' minute
ORDER BY seconds_after ASC
LIMIT 500;
