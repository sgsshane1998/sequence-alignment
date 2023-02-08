import os
import sys
import psutil
import argparse
import time
from copy import deepcopy
import math

dp1 = []
dp2 = []
result_pairs = []

#delta penalty
Delta = 30

# alpha penalty
Alpha = {}
Alpha["A"] = {"A": 0, "C": 110, "G": 48, "T": 94}
Alpha["C"] = {"A": 110, "C": 0, "G": 118, "T": 48}
Alpha["G"] = {"A": 48, "C": 118, "G": 0, "T": 110}
Alpha["T"] = {"A": 94, "C": 48, "G": 110, "T": 0}

def parse_input(file_name):
    with open(file_name) as f:
        cont = f.read().splitlines()
    for i in range(1, len(cont)):
        if not cont[i].isdigit():
            split_index = i
    return cont[0], [int(idx) for idx in cont[1:split_index]], cont[split_index], [int(index) for index in cont[1 + split_index:]]

def parse_base(base_string, ls_indices):
    base = base_string
    for i in ls_indices:
        base = base[: i + 1] + base + base[i + 1:]
    assert len(base) == (2 ** len(ls_indices)) * len(base_string)
    return base

def string_alignment(s1, s2):
    col_size = len(s1) + 1
    row_size = len(s2) + 1
    dp = [[0] * row_size for i in range(col_size)]
    
    #set base case
    for i in range(col_size):
        dp[i][0] = i * Delta
    for i in range(row_size):
        dp[0][i] = i * Delta

    #general dp process
    for i in range(1, col_size):
        for j in range(1, row_size):
            mismatch = dp[i - 1][j - 1] + Alpha[s1[i - 1]][s2[j - 1]]
            gap_top = dp[i - 1][j] + Delta
            gap_left = dp[i][j - 1] + Delta
            dp[i][j] = min(mismatch, gap_top, gap_left)
    
    #find minimum cost alignment
    s1_align = ''
    s2_align = ''
    ls1 = len(s1)
    ls2 = len(s2)
    while ls1 != 0 and ls2 != 0:
        if dp[ls1][ls2] == dp[ls1 - 1][ls2 - 1] + Alpha[s1[ls1 - 1]][s2[ls2 - 1]]:
            s1_align = s1[ls1 - 1] + s1_align
            s2_align = s2[ls2 - 1] + s2_align
            ls1 = ls1 - 1
            ls2 = ls2 - 1
        elif dp[ls1][ls2] == dp[ls1 - 1][ls2] + Delta:
            s1_align = s1[ls1 - 1] + s1_align
            s2_align = '_' + s2_align
            ls1 = ls1 - 1
        else:
            s1_align = '_' + s1_align
            s2_align = s2[ls2 - 1] + s2_align
            ls2 = ls2 - 1

    #assign gap for the rest
    if ls1 != 0:
        for i in range(ls1, 0, -1):
            s1_align = s1[i - 1] + s1_align
            s2_align = '_' + s2_align
    elif ls2 != 0:
        for i in range(ls2, 0, -1):
            s1_align = '_' + s1_align
            s2_align = s2[i - 1] + s2_align

    return [s1_align, s2_align]


def forward_alignment(s1, s2):

    for i in range(len(s1) + 1):
        dp1[i][0] = i * Delta

    for j in range(1, len(s2) + 1):
        dp1[0][1] = j * Delta
        for i in range(1, len(s1) + 1):
            dp1[i][1] = min(
                dp1[i - 1][0] + Alpha[s1[i - 1]][s2[j - 1]],
                dp1[i - 1][1] + Delta,
                dp1[i][0] + Delta,
            )

        for k in range(len(s1) + 1):
            dp1[k][0] = dp1[k][1]
    return deepcopy(dp1[: len(s1) + 1])


def backward_alignment(s1, s2):

    for i in range(len(s1) + 1):
        dp2[i][0] = (len(s1) - i) * Delta

    for j in range(len(s2) - 1, -1, -1):
        dp2[len(s1)][1] = (len(s2) - j) * Delta
        for i in range(len(s1) - 1, -1, -1):
            dp2[i][1] = min(
                dp2[i + 1][0] + Alpha[s1[i]][s2[j]],
                dp2[i + 1][1] + Delta,
                dp2[i][0] + Delta,
            )

        for k in range(len(s1) + 1):
            dp2[k][0] = dp2[k][1]
    return deepcopy(dp2[: len(s1) + 1])




def divide_conquer_align(s1, s2):
    if len(s1) <= 2 or len(s2) <= 2:
        result_pairs.append(string_alignment(s1, s2))
        return

    split_index = math.floor(len(s2) / 2)

    forward = forward_alignment(s1, s2[:split_index])
    backword = backward_alignment(s1, s2[split_index:])

    base_value = forward[0][1] + backword[0][1]
    cut_index = 0
    for i in range(len(s1) + 1):
        sum_value = forward[i][1] + backword[i][1]
        base_value = min(base_value, sum_value)
        if sum_value < base_value:
            base_value = sum_value
            cut_index = i
    #recusive method to make alignments to different cuts
    divide_conquer_align(s1[ : cut_index], s2[0 : split_index])
    divide_conquer_align(s1[cut_index:], s2[split_index: ])

def extract_alignments():
    s1_alignment = ''.join([p[0] for p in result_pairs])
    s2_alignment = ''.join([p[1] for p in result_pairs])
    return s1_alignment, s2_alignment

def get_cost(s1, s2):
    cost = 0
    for i in range(len(s1)):
        if s1[i] != "_" and s2[i] != "_":
            cost += Alpha[s1[i]][s2[i]]
        else:
            cost += Delta
    return cost

def write_output_file(
    s1, s2, solution_cost, time_taken, memory_used, filename="output_1_t.txt"):
    with open(filename, "w") as f:
        f.write(f"{solution_cost}")
        f.write("\n")
        f.write(f"{s1}")
        f.write("\n")
        f.write(f"{s2}")
        f.write("\n")
        f.write(f"{time_taken}")
        f.write("\n")
        f.write(f"{memory_used}")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", type=str)
    args = parser.parse_args()

    base1, lst1, base2, lst2 = parse_input(args.file_name)

    sequence_one = parse_base(base1, lst1)
    sequence_two = parse_base(base2, lst2)

    start = time.time()

    dp1 = [[0, 0] for _ in range(len(sequence_one) + 1)]
    dp2 = [[0, 0] for _ in range(len(sequence_two) + 1)]
    divide_conquer_align(sequence_one, sequence_two)
    
    s1_align, s2_align = extract_alignments()

    cost = get_cost(s1_align, s2_align)

    memory_info = psutil.Process().memory_info()
    memory_cost = float(memory_info.rss/1024)
    end_at = time.time()
    time_cost = (end_at - start) * 1000
    write_output_file(s1_align, s2_align, cost, time_cost, memory_cost)