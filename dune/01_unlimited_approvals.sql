-- 01_unlimited_approvals.sql
-- KYT dashboard metric #1: daily volume of UNLIMITED ERC-20 approvals to
-- contracts that are NOT in a small known-routers exclusion list.
-- High-volume baseline + outliers are what a monitoring team watches.
-- DuneSQL (Ethereum). Adjust table names if your Dune schema version differs.

WITH unlim AS (
  SELECT
    date_trunc('day', evt_block_time) AS day,
    contract_address,
    owner,
    spender
  FROM ethereum."ERC20_evt_Approval"
  WHERE evt_block_time >= now() - interval '90' day
    AND value = 57896044618658097711785492504343953926634992332820282019728792003956564819935  -- 2^256-1
    AND spender NOT IN (
      0x111111125421cA6dc452d289314280a0f8842A65,  -- 1inch v6
      0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45,  -- Uniswap V3 router
      0x00000000006cBfC000B2C6E1aB4E8c5e4b5b5b5b   -- (extend your own list)
    )
)
SELECT day,
       count(*)                       AS unlimited_approvals,
       count(DISTINCT spender)        AS distinct_spenders,
       count(DISTINCT owner)          AS distinct_owners
FROM unlim
GROUP BY day
ORDER BY day DESC;
