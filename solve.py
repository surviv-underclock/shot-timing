import itertools

REQUIRE_SHOT_AT_ZERO = False
FREE_SWITCH_TIMER = 1000
FREE_SWITCH_DELAY = 250
SWITCH_DELAY = (900, 300)
DEPLOY_GROUP = (1, -2) # do not use 0; also, use -1 and -2 for "no deploy group"
MAG_SIZE = (5, 2)
# MAX_SLOW_PENALTY = 0
# FIRE_DELAY = (0, 0)

WEAP_NAMES = ['M870', 'MP220']

def remove_one_shot(s, i):
    return s[:i] + (s[i] - 1,) + s[i + 1:]

def solve(fs_timer, deploy_group, s, memo = {}):
    if not any(s):
        return 0, 1, ((),)

    key = (fs_timer,) + s
    if key not in memo:
        best = best_count = best_chains = None
        for i in range(len(s)):
            if not s[i]:
                continue

            ns = remove_one_shot(s, i)

            delay_fs = fs_timer
            if delay_fs == 0 and DEPLOY_GROUP[i] == deploy_group:
                delay_fs = FREE_SWITCH_TIMER
            delay_fs += FREE_SWITCH_DELAY

            switch_delay = SWITCH_DELAY[i]
            for delay, next_fs, was_fs in (
                (delay_fs, FREE_SWITCH_TIMER - FREE_SWITCH_DELAY, True), # next free switch
                (switch_delay, fs_timer - switch_delay if fs_timer >= switch_delay else FREE_SWITCH_TIMER, False), # switch delay
            ):
                r, count, chains = solve(next_fs, DEPLOY_GROUP[i], ns)
                r += delay
                if best is None or best > r:
                    best, best_count, best_chains = r, count, tuple(((i, delay, next_fs, was_fs),) + x for x in chains)
                elif best == r:
                    best_count += count
                    best_chains += tuple(((i, delay, next_fs, was_fs),) + x for x in chains)
        memo[key] = best, best_count, best_chains

    return memo[key]

def solve2(s, initial_fs, initial_was_fs):
    initial_delay = FREE_SWITCH_TIMER - initial_fs

    best = best_count = best_chains = None
    for i in range(len(s)):
        if not s[i]:
            continue

        r, count, chains = solve(initial_fs, 0, remove_one_shot(s, i))
        if best is None or best > r:
            best, best_count, best_chains = r, count, tuple(((i, initial_delay, initial_fs, initial_was_fs),) + x for x in chains)
        elif best == r:
            best_count += count
            best_chains += tuple(((i, initial_delay, initial_fs, initial_was_fs),) + x for x in chains)

    if best is None:
        return 0, 1, ((),)

    return best, best_count, best_chains

def minimize_time_first_to_last(s):
    if REQUIRE_SHOT_AT_ZERO:
        return solve2(s, FREE_SWITCH_TIMER, False)
    else:
        return solve2(s, 1, True)

def minimize_max_time_between_shots():
    raise NotImplementedError('this problem is hard')

def format_timings(chain):
    entries = []
    not_first = False
    for v in chain:
        if v[3] and not_first:
            if v[1] != FREE_SWITCH_DELAY:
                entries.append(str(v[1] - FREE_SWITCH_DELAY))
            entries.append('fs {}'.format(FREE_SWITCH_DELAY))
        else:
            entries.append(str(v[1]))
        entries.append(WEAP_NAMES[v[0]])
        not_first = True
    return ' '.join(entries)

def format_instructions(chain):
    t = 0
    last_weap = None
    tokens = []
    for shot in chain:
        t += shot[1]
        if shot[3]:
            if shot[1] != FREE_SWITCH_DELAY and t != 999:
                tokens.append('c')
                tokens.append(str(t - FREE_SWITCH_DELAY) + ':')
            tokens.append(chr(ord('A') + shot[0]))
            tokens.append(str(t) + ':')
            tokens.append('!')
        else:
            if last_weap == shot[0]:
                tokens.append('d')
            tokens.append(chr(ord('a') + shot[0]))
            tokens.append(str(t) + ':')
            tokens.append('!')
        last_weap = shot[0]
    return ' '.join(tokens)

best, best_count, best_chains = minimize_time_first_to_last(MAG_SIZE)
print(best_count)
print(best)
for chain in best_chains:
    print()
    print(format_timings(chain))
    print(format_instructions(chain))
