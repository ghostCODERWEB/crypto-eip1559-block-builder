"""Simulate nonce-constrained fee-priority packing, base-fee updates, fee burning and validator tips."""

from .validation import integer, identifier
import copy


def next_base_fee(base, used, limit):
    base = integer(base)
    used = integer(used)
    limit = integer(limit, minimum=2)
    target = limit // 2
    if used > limit:
        raise ValueError("gas exceeds limit")
    if used == target:
        return base
    if used > target:
        return base + max(base * (used - target) // target // 8, 1)
    return base - base * (target - used) // target // 8


def analyze(data):
    base = integer(data["initial_base_fee"])
    limit = integer(data["gas_limit"], minimum=2)
    nonces = {identifier(k): integer(v) for k, v in data.get("nonces", {}).items()}
    pending = []
    ids = set()
    slots = set()
    for tx in data["transactions"]:
        key = identifier(tx["id"])
        owner = identifier(tx["sender"])
        nonce = integer(tx["nonce"])
        gas = integer(tx["gas"], minimum=1, maximum=limit)
        cap = integer(tx["max_fee"])
        tip = integer(tx["priority_fee"])
        if key in ids or (owner, nonce) in slots or tip > cap:
            raise ValueError("duplicate transaction/nonce or invalid fee cap")
        ids.add(key)
        slots.add((owner, nonce))
        pending.append(
            {
                "id": key,
                "sender": owner,
                "nonce": nonce,
                "gas": gas,
                "max_fee": cap,
                "priority_fee": tip,
            }
        )
    blocks = []
    burned = 0
    tips = 0
    for index in range(integer(data.get("block_count", 3), minimum=1, maximum=100)):
        used = 0
        included = []
        while True:
            eligible = [
                t
                for t in pending
                if t["nonce"] == nonces.get(t["sender"], 0)
                and t["max_fee"] >= base
                and t["gas"] + used <= limit
            ]
            if not eligible:
                break
            eligible.sort(
                key=lambda t: (-min(t["priority_fee"], t["max_fee"] - base), t["id"])
            )
            tx = eligible[0]
            tip = min(tx["priority_fee"], tx["max_fee"] - base)
            cost = tx["gas"] * (base + tip)
            used += tx["gas"]
            nonces[tx["sender"]] = tx["nonce"] + 1
            pending.remove(tx)
            burned += tx["gas"] * base
            tips += tx["gas"] * tip
            included.append({**tx, "effective_tip": tip, "cost": cost})
        following = next_base_fee(base, used, limit)
        blocks.append(
            {
                "index": index,
                "base_fee": base,
                "gas_used": used,
                "next_base_fee": following,
                "transactions": included,
            }
        )
        base = following
    return {
        "blocks": blocks,
        "pending": pending,
        "nonces": nonces,
        "burned": burned,
        "validator_tips": tips,
        "total_transaction_cost": burned + tips,
        "final_base_fee": base,
    }
