from functools import reduce

from lite_dist2.interfaces import Mergeable
from lite_dist2.value_models.space import ParameterAlignedSpace


def simplify[T: Mergeable](mergeables: list[T], *args: object) -> list[T]:
    new_aps: list[Mergeable] = []
    mergeables_duplicated_group: dict[int, set[int]] = {}
    sub_space_num = len(mergeables)

    for i in range(sub_space_num):
        for j in range(i + 1, sub_space_num):
            if mergeables[i].can_merge(mergeables[j], *args):
                if i in mergeables_duplicated_group:
                    mergeables_duplicated_group[i].add(j)
                else:
                    mergeables_duplicated_group[i] = {j}

    mergeable_group: list[set[int]] = []
    for i, mergeable_to_i in mergeables_duplicated_group.items():
        grouplet = mergeable_to_i.union({i})
        for g in range(len(mergeable_group)):
            intersection = mergeable_group[g].intersection(grouplet)
            if len(intersection) > 0:
                mergeable_group[g] = mergeable_group[g].union(grouplet)
                break
        else:
            mergeable_group.append(grouplet)

    not_mergeables = set(range(sub_space_num)) - reduce(lambda x, y: x.union(y), mergeable_group, set())
    new_aps.extend([mergeables[i] for i in not_mergeables])

    for group_index_set in mergeable_group:
        group_space_list = sorted([mergeables[i] for i in group_index_set], key=lambda spc: spc.get_start_index(*args))
        merged = group_space_list[0]
        for space in group_space_list[1:]:
            merged = merged.merge(space, *args)
        new_aps.append(merged)

    return sorted(new_aps, key=lambda spc: spc.get_start_index(*args))


def remap_space(aps: list[ParameterAlignedSpace], dim: int) -> dict[int, list[ParameterAlignedSpace]]:
    remapped = {i: [] for i in range(-1, dim)}

    for space in aps:
        universal_dim = space.get_lower_not_universal_dim()
        remapped[universal_dim].append(space)
    return remapped
