'''
    Description: This file implements the algorithm to obtain Longest Common Subsequence of Multiple 
        Sequences (MLCS), which is modified based on the C++ implementation of the algorithm available at:
        https://github.com/qwangmsk/MLCS-Astar
    Author: LogPAI team
    License: MIT
'''

import numpy as np
import re


def sorted_partition(nums, d):
    dim = len(nums[0]) - d
    mid_d_value = nums[len(nums) // 2][dim]
    bound = len(nums)
    for x in reversed(nums):
        bound -= 1
        if x[dim] == mid_d_value:
            break
    return nums[:bound], nums[bound:]


def dominate_points_2d(nums):
    dom_points = []
    max_y_value = float('Inf')
    for p in nums:
        if p[1] < max_y_value:
            dom_points.append(p)
            max_y_value = p[1]
    return dom_points


def union(nums, d, dic):
    if len(nums) <= 1:
        return nums
    nums = sorted(nums, key=lambda x: x[len(x) - d:])
    if d == 2:
        res_2d = []
        min_y = float("inf")
        black_found = False
        for x in nums:
            if dic[x] == 'black':
                black_found = True
                res_2d.append(x)
                min_y = min(x[-1], min_y)
            elif x[-1] < min_y or not black_found:
                res_2d.append(x)
        return res_2d

    lhs, rhs = sorted_partition(nums, d)
    lhs_min = union(lhs, d, dic)
    rhs_min = union(rhs, d, dic)

    cross = [x for x in lhs_min if dic[x] == 'black'] + [x for x in rhs_min if dic[x] != 'black']
    cross_min = union(cross, d - 1, dic)
    ret = list(set(lhs_min + cross_min + [x for x in rhs_min if dic[x] == 'black']))
    return ret


def min_points(nums, d):
    if len(nums) <= 1:
        return nums

    nums = sorted(nums, key=lambda x: x[len(x) - d:])
    if d == 2:
        return dominate_points_2d(nums)

    lhs, rhs = sorted_partition(nums, d)
    lhs_min = min_points(lhs, d)
    rhs_min = min_points(rhs, d)

    dic = {}
    for e in lhs_min:
        dic[e] = 'black'
    for e in rhs_min:
        dic[e] = 'white'
    ret = union(lhs_min + rhs_min, d - 1, dic)
    return ret


def get_alphabet(seq):
    return set([x for j in seq for x in j])


def get_preprocessing_matrix(alphabet, seq):
    if not seq:
        return
    row_size = max([len(x) for x in seq])
    matrix = np.ones((len(alphabet), row_size, len(seq)), dtype=np.int) * (row_size + 1)
    for (s_index, s) in enumerate(alphabet):
        for j in range(row_size):
            for i in range(len(seq)):
                if s == 'a':
                    x = []
                try:
                    first_occur = seq[i].index(s, j)
                    matrix[s_index][j][i] = first_occur
                except ValueError:
                    continue
    return matrix


def get_parents(q, alphabet, mat):
    parents = []
    for s_index, s in enumerate(alphabet):
        try:
            p = [mat[s_index][q[i] + 1][i] for i, x in enumerate(list(q))]
            p = tuple(p)
        except IndexError:
            break
        if p != q and len(mat[0]) + 1 not in p:
            parents.append(p)
    return parents


# compute dominant points
def get_mult_lcs(seq):
    if not seq:
        return
    alph = get_alphabet(seq)
    T = get_preprocessing_matrix(alph, seq)
    rank = len(seq)
    dominant_points = [[tuple([-1] * rank)]]
    k = 0

    while dominant_points[k]:
        par_s = dict([(letter, []) for letter in alph])
        for q in dominant_points[k]:
            all_pars = get_parents(q, alph, T)
            dom_b = min_points(all_pars, rank)
            for s_index, s in enumerate(alph):
                try:
                    p = [T[s_index][q[i] + 1][i] for i, x in enumerate(list(q))]
                    p = tuple(p)
                except IndexError:
                    continue
                if p in dom_b and p not in par_s[s] and len(T[0]) + 1 not in p:
                    par_s[s].append(p)
        values_pars = []
        for s_pars in par_s.values():
            values_pars = values_pars + s_pars
        new_dom_k = min_points(values_pars, rank)
        dominant_points.append(new_dom_k)
        k += 1

    # k = 1, no common pattern
    if k == 1:
        return ''
    p = dominant_points[k - 1][0]

    rlcs = [seq[0][p[0]]]
    while k > 2:
        k -= 1
        q = p
        for e in dominant_points[k - 1]:
            if p in get_parents(e, alph, T):
                q = e
        p = q
        rlcs.append(seq[0][p[0]])

    mlcs = rlcs[::-1]
    return mlcs


def get_common_pattern(str_list):
    comment_seq = get_mult_lcs(str_list)
    if not comment_seq or not str_list:
        return ''
    cur_pattern_list = list(comment_seq)
    new_pattern_list = []
    for seq in str_list:
        seq_list = list(seq)
        cur_index = 0
        for (index_e, e) in enumerate(cur_pattern_list):
            if e != '[*]':
                if e != seq_list[cur_index]:
                    new_pattern_list.append('[*]')
                    cur_index = seq_list.index(e, cur_index) + 1
                else:
                    cur_index += 1
                new_pattern_list.append(e)
            else:
                new_pattern_list.append('[*]')
                try:
                    cur_index = seq_list.index(cur_pattern_list[index_e + 1], cur_index)
                except IndexError:
                    break
        if cur_index < len(seq_list) and cur_pattern_list[-1] != '[*]':
            new_pattern_list.append('[*]')
        cur_pattern_list = new_pattern_list
        new_pattern_list = []
    final_pattern = ''.join(cur_pattern_list)
    final_pattern = re.sub(r'\[\*\](\s\[\*\])+', '[*]', final_pattern)
    return final_pattern


if __name__ == '__main__':
    # Test example
    sequences = [['abc', '123', 'def'], ['abc', '345', 'def']] 
    com_pattern = get_common_pattern(sequences)
    print(com_pattern)

