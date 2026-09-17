-- 01_unlimited_approvals.sql  (v2: raw-logs version, most robust)
-- KYT dashboard metric #1: daily count of UNLIMITED ERC-20 approvals.
-- Uses the RAW logs table (ethereum.logs), which exists on every chain,
-- instead of a decoded table whose name varies by Dune schema version.
--   Approval event topic0 = keccak256("Approval(address,address,uint256)")
--   data = the allowance uint256. Unlimited = 2^256-1 = 32 bytes of 0xff.
-- Comparing varbinary directly avoids the huge-integer literal problem.

SELECT
  date_trunc('day', block_time) AS day,
  count(*)                       AS unlimited_approvals,
  count(DISTINCT contract_address) AS distinct_tokens
FROM ethereum.logs
WHERE topic0 = 0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925
  AND data  = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
  AND block_time >= now() - interval '90' day
GROUP BY 1
ORDER BY 1 DESC;
