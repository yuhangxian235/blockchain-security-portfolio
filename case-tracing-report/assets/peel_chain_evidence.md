# Peel-Chain Detector — Evidence

Tool: `python-detection/detect_peel_chain.py`
Root (known July-2026 mule): `0x6040E865152db6E833105D86d086fb7FA5b97534`

## Run output
```
- 0x6040...  nonce=3  out-chunks=3  peel-score=4/8  [fresh/one-use, 3 chunks]
    -> 0x33145...  282.39 ETH
    -> 0x24698...  103.77 ETH
    -> 0xc1695...  17.64 ETH
  - 0x24698...  nonce=0  out-chunks=0  score=2/8  [fresh/one-use]
  - 0xc1695...  nonce=1  out-chunks=1  score=2/8
      -> 0x81cef...  17.64 ETH
  - 0x33145...  nonce=2  out-chunks=1  score=2/8
      -> 0x05aeb...  282.29 ETH
```

## What it shows
The tool, given only the root mule address, automatically rebuilt the layering
tree we first traced by hand in MistTrack:
mule -> {282.39 -> 0x33145 -> 0x05aeb, 103.77 -> 0x24698, 17.64 -> 0xc1695 -> 0x81cef}.
Every node is a fresh/one-use EOA (nonce 0-3).

## Tuning insight (analytical note)
The root scored 4/8, below the >=5 threshold, because the three chunks are NOT
equal (282 vs 17.64 ETH). Real peel chains often "peel off the largest remainder
each hop" rather than split evenly. Lesson logged: add a "large remainder forwarded
to a fresh node" signal alongside the equal-size (low-CV) signal. This is the kind
of rule-tuning a KYT analyst does daily.

## Score key (0-8)
+2 fresh/one-use (nonce <= 8) | +2 splits >=2 chunks | +2 similar-sized (CV<0.6) |
+2 child also splits. >=5 likely automated layering.
