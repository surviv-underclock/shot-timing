# shot-timing
Optimize shot timings in surviv.io

## Program
The program takes the following inputs and outputs the optimal objective value and sequence of instructions:
- objective: minimize `maximum time between adjacent shots`, or `time from first to last shot`
- require shot at time zero: `yes`/`no`
- switch delay 1, switch delay 2
- mag size 1, mag size 2
- maximum slow penalty duration (0 for desync/overclock, infinity for maxfiring)
- fire delay 1, fire delay 2 (not needed if maximum slow penalty duration is 0)

## Algorithms
### Minimize `time from first to last shot`
This is implemented with brute-force and memoization, which is effectively top-down dynamic programming.

At any time, there are only two decisions:
- which gun to shoot
- whether to `wait out full switch delay` or `wait for next free switch`

The state is `ammo count 1`, `ammo count 2`, `current deploy group`, and `free switch timer`.

### Minimize `maximum time between adjacent shots`
This feature is not yet implemented.

## Macro Generation
It is possible to take the output and create a macro to execute the instructions, but due to network latency, it is often better to tweak the timings manually.

This project has not yet implemented macro generation.
