def normalize_total(total_weighted, weight_sum):
    if weight_sum <= 0: return 0.0

    if 0.99 <= weight_sum <= 1.01:
        return total_weighted

    if 99 <= weight_sum <= 101:
        return total_weighted / 100.0

    return total_weighted / weight_sum


def to_5pt(percent):
    if percent is None:
        return 2
    if percent >= 85: return 5
    if percent >= 70: return 4
    if percent >= 50: return 3
    return 2