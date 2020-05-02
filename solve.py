from typing import NamedTuple, Tuple

class Weapon(NamedTuple):
    name: str
    switch_delay: int
    deploy_group: int # do not use 0; also, use -1 and -2 for "no deploy group"
    mag_size: int
    fire_delay: int = 0

class Solver(NamedTuple):
    weapons: Tuple[Weapon]
    require_shot_at_zero = False
    free_switch_timer = 1000
    free_switch_delay = 250
    max_slow = 0
    memo: dict

    @classmethod
    def new(cls, *args, **kwargs):
        return cls(memo={}, *args, **kwargs)

    def minimize_time_first_to_last(self):
        s = self._get_shots_initial()
        if self.require_shot_at_zero:
            return self._solve2(s, 0, 0, False)
        else:
            return self._solve2(s, 1, self.free_switch_timer - 1, True)

    def minimize_max_time_between_shots(self):
        raise NotImplementedError('this problem is hard')

    def _get_shots_initial(self):
        return tuple(w.mag_size for w in self.weapons)

    def _solve(self, fs_timer, deploy_group, s):
        if not any(s):
            return 0, 1, ((),)

        key = (fs_timer, deploy_group) + s
        if key not in self.memo:
            best = best_count = best_chains = None
            for i, weap in enumerate(self.weapons):
                if not s[i]:
                    continue

                next_s = Solver.remove_one_shot(s, i)

                for delay, next_fs, was_fs in (
                    # wait for next free switch
                    (
                        (self.free_switch_timer if fs_timer == 0 and weap.deploy_group == deploy_group else fs_timer)
                            + self.free_switch_delay,
                        self.free_switch_timer - self.free_switch_delay,
                        True
                    ),
                    # use full switch delay
                    (
                        weap.switch_delay,
                        max(0, (fs_timer or self.free_switch_timer) - weap.switch_delay),
                        False
                    ),
                ):
                    r, count, chains = self._solve(next_fs, weap.deploy_group, next_s)
                    r += delay
                    if best is None or best > r:
                        best, best_count, best_chains = r, count, tuple(((i, delay, next_fs, was_fs),) + x for x in chains)
                    elif best == r:
                        best_count += count
                        best_chains += tuple(((i, delay, next_fs, was_fs),) + x for x in chains)
            self.memo[key] = best, best_count, best_chains

        return self.memo[key]

    def _solve2(self, s, initial_fs, initial_delay, initial_was_fs):
        best = best_count = best_chains = None
        for i, weap in enumerate(self.weapons):
            if not s[i]:
                continue

            r, count, chains = self._solve(initial_fs, weap.deploy_group, Solver.remove_one_shot(s, i))
            if best is None or best > r:
                best, best_count, best_chains = r, count, tuple(((i, initial_delay, initial_fs, initial_was_fs),) + x for x in chains)
            elif best == r:
                best_count += count
                best_chains += tuple(((i, initial_delay, initial_fs, initial_was_fs),) + x for x in chains)

        if best is None:
            return 0, 1, ((),)

        return best, best_count, best_chains

    @staticmethod
    def remove_one_shot(s, i):
        return s[:i] + (s[i] - 1,) + s[i + 1:]

class Formatter(NamedTuple):
    solver: Solver

    def format(self, chain) -> str:
        raise NotImplementedError

class TimingFormatter(Formatter):
    def format(self, chain):
        entries = []
        not_first = False
        for v in chain:
            if v[3] and not_first:
                if v[1] != self.solver.free_switch_delay:
                    entries.append(str(v[1] - self.solver.free_switch_delay))
                entries.append('fs {}'.format(self.solver.free_switch_delay))
            elif v[1] or not_first:
                entries.append(str(v[1]))
            entries.append(self.solver.weapons[v[0]].name)
            not_first = True
        return ' '.join(entries)

class InstructionFormatter(Formatter):
    def format(self, chain):
        t = 0
        last_weap = None
        not_first = False
        tokens = []
        for shot in chain:
            t += shot[1]
            if shot[3]:
                if shot[1] != self.solver.free_switch_delay and not_first:
                    tokens.append('c')
                    tokens.append(str(t - self.solver.free_switch_delay) + ':')
                tokens.append(chr(ord('A') + shot[0]))
                tokens.append(str(t) + ':')
                tokens.append('!')
            else:
                if last_weap == shot[0]:
                    tokens.append('d')
                tokens.append(chr(ord('a') + shot[0]))
                if t:
                    tokens.append(str(t) + ':')
                tokens.append('!')
            last_weap = shot[0]
            not_first = True
        return ' '.join(tokens)

def main():
    solver = Solver.new(weapons=(
        Weapon('M870', 900, 1, 5),
        Weapon('MP220', 300, -2, 2),
    ))

    formatters = (TimingFormatter(solver), InstructionFormatter(solver))

    best, best_count, best_chains = solver.minimize_time_first_to_last()
    print(best_count)
    print(best)
    for chain in best_chains:
        print()
        for formatter in formatters:
            print(formatter.format(chain))

if __name__ == '__main__':
    main()
