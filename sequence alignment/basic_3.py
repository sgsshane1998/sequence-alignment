import os
import sys
import psutil
import argparse
import time

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

    return dp[len(s1)][len(s2)], s1_align, s2_align

def output_file(s1, s2, cost, time_cost, memory_cost, out_file = 'b_output_11t.txt'):
    with open(out_file, "w") as f:
        f.write(f"{cost}")
        f.write("\n")
        f.write(f"{s1}")
        f.write("\n")
        f.write(f"{s2}")
        f.write("\n")
        f.write(f"{time_cost}")
        f.write("\n")
        f.write(f"{memory_cost}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', type=str)
    args = parser.parse_args()
    base1, lst1, base2, lst2 = parse_input(args.file_name)

    sequence_one = parse_base(base1, lst1)
    sequence_two = parse_base(base2, lst2)

    start_at = time.time()
    cost, s1_align, s2_align = string_alignment(sequence_one, sequence_two)
    
    memory_info = psutil.Process().memory_info()
    memory_cost = float(memory_info.rss/1024)
    
    time_cost = (time.time() - start_at) * 1000
    output_file(s1_align, s2_align, cost, time_cost, memory_cost)
