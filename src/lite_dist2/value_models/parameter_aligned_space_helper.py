from functools import reduce

from lite_dist2.value_models.space import ParameterAlignedSpace


def simplify_table_by_dim(aps: list[ParameterAlignedSpace], target_dim: int) -> list[ParameterAlignedSpace]:
    new_aps: list[ParameterAlignedSpace] = []
    mergeables: dict[int, set[int]] = {}
    sub_space_num = len(aps)

    for i in range(sub_space_num):
        for j in range(i + 1, sub_space_num):
            if aps[i].can_merge(aps[j], target_dim):
                if i in mergeables:
                    mergeables[i].add(j)
                else:
                    mergeables[i] = {j}

    mergeable_group: list[set[int]] = []
    for i, mergeable_to_i in mergeables.items():
        grouplet = mergeable_to_i.union({i})
        for g in range(len(mergeable_group)):
            intersection = mergeable_group[g].intersection(grouplet)
            if len(intersection) > 0:
                mergeable_group[g] = mergeable_group[g].union(grouplet)
                break
        else:
            mergeable_group.append(grouplet)

    not_mergeables = set(range(sub_space_num)) - reduce(lambda x, y: x.union(y), mergeable_group, set())
    new_aps.extend([aps[i] for i in not_mergeables])

    for group_index_set in mergeable_group:
        group_space_list = sorted([aps[i] for i in group_index_set], key=lambda spc: spc.axes[target_dim].start)
        merged = group_space_list[0]
        for space in group_space_list[1:]:
            merged = merged.merge(space)
        new_aps.append(merged)

    return sorted(new_aps, key=lambda spc: spc.axes[target_dim].start)
