
from dataclasses import dataclass
import math
from typing import Dict, List, Tuple

@dataclass
class UAV:
    name: str
    channel_factor: float
    qos_requirement: float
    x: float

# IMPORTANT:
# This is a simplified Open Lab model intended for visualization and interaction.
# It is NOT a numerical reproduction of the paper/thesis model.
#
# Simplified rate model:
#   snr_i(n) = SNR_SCALE * channel_factor_i * n^2
#   rate_i(n) = log2(1 + snr_i(n))
#
# The n^2 scaling is used only to create an intuitive "more OIRS blocks -> stronger link"
# relationship in this educational demo. Replace this model with your exact equations or
# precomputed simulation results before using the demo for quantitative research claims.

SNR_SCALE = 1.00

SCENARIOS: Dict[str, List[UAV]] = {
    "Balanced links": [
        UAV("UAV 1", 0.085, 4.0, -3.0),
        UAV("UAV 2", 0.078, 4.0, -1.0),
        UAV("UAV 3", 0.092, 4.0,  1.0),
        UAV("UAV 4", 0.081, 4.0,  3.0),
    ],
    "One weak UAV": [
        UAV("UAV 1", 0.085, 4.0, -3.0),
        UAV("UAV 2", 0.075, 4.0, -1.0),
        UAV("UAV 3", 0.022, 4.0,  1.0),
        UAV("UAV 4", 0.080, 4.0,  3.0),
    ],
    "Different QoS demands": [
        UAV("UAV 1", 0.084, 3.2, -3.0),
        UAV("UAV 2", 0.068, 5.0, -1.0),
        UAV("UAV 3", 0.058, 4.0,  1.0),
        UAV("UAV 4", 0.079, 5.6,  3.0),
    ],
}

def rate(channel_factor: float, n_blocks: int) -> float:
    if n_blocks <= 0:
        return 0.0
    snr = SNR_SCALE * channel_factor * (n_blocks ** 2)
    return math.log2(1.0 + snr)

def min_blocks_for_qos(channel_factor: float, qos_requirement: float, max_blocks: int = 500) -> int:
    for n in range(1, max_blocks + 1):
        if rate(channel_factor, n) >= qos_requirement:
            return n
    return max_blocks + 1

def equal_allocation(uavs: List[UAV], total_blocks: int) -> List[int]:
    m = len(uavs)
    base = total_blocks // m
    rem = total_blocks % m
    return [base + (1 if i < rem else 0) for i in range(m)]

def qos_aware_allocation(uavs: List[UAV], total_blocks: int) -> List[int]:
    """
    Simplified QoS-first allocation:
    1) Compute the minimum blocks each UAV needs to meet its QoS.
    2) Admit UAVs in ascending order of required blocks, maximizing the number
       of UAVs that can be satisfied with the limited budget.
    3) Allocate remaining blocks one-by-one to the UAV with the largest
       marginal rate gain.
    """
    m = len(uavs)
    alloc = [0] * m
    need = [min_blocks_for_qos(u.channel_factor, u.qos_requirement) for u in uavs]

    admitted = []
    remaining = total_blocks

    for i in sorted(range(m), key=lambda idx: need[idx]):
        if need[i] <= remaining:
            alloc[i] = need[i]
            remaining -= need[i]
            admitted.append(i)

    # If no UAV can be admitted, start from zero and use marginal-gain allocation.
    # Otherwise distribute residual blocks across all UAVs.
    for _ in range(remaining):
        gains = []
        for i, u in enumerate(uavs):
            current = rate(u.channel_factor, alloc[i])
            nxt = rate(u.channel_factor, alloc[i] + 1)
            gains.append(nxt - current)
        j = max(range(m), key=lambda idx: gains[idx])
        alloc[j] += 1

    return alloc

def evaluate(uavs: List[UAV], alloc: List[int]) -> Dict:
    rates = [rate(u.channel_factor, n) for u, n in zip(uavs, alloc)]
    satisfied = [r >= u.qos_requirement for r, u in zip(rates, uavs)]
    return {
        "rates": rates,
        "satisfied": satisfied,
        "num_satisfied": sum(satisfied),
        "total_rate": sum(rates),
    }

def scenario_explanation(name: str) -> str:
    if name == "Balanced links":
        return (
            "The UAV links have similar conditions. Equal allocation is already competitive, "
            "so the benefit of QoS-aware allocation is usually smaller."
        )
    if name == "One weak UAV":
        return (
            "One UAV has a much weaker optical link. This scenario shows why blindly giving "
            "every UAV the same number of OIRS blocks can be inefficient."
        )
    return (
        "The UAVs have different QoS targets. The allocator must decide how to use the limited "
        "OIRS resource while considering both link quality and service requirements."
    )
