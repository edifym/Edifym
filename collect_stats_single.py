import sys

from CommandHelper import CommandHelper


if __name__ == "__main__":
    stats_static = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats_static.txt'], './').splitlines()
    stats_dynamic = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats_dynamic.txt'], './').splitlines()

    if len(stats_static) != 27:
        print(f'static stats incorrect stats length {len(stats_static)} {stats_static}')
        sys.exit(-1)

    if len(stats_dynamic) != 27:
        print(f'static stats incorrect stats length {len(stats_dynamic)} {stats_dynamic}')
        sys.exit(-1)

    totals_static = 0
    totals_dynamic = 0
    prev_time = 0

    for i in range(26):
        if i % 2 == 0:
            prev_time = int(stats_static[i][2:])
        else:
            totals_static += int(stats_static[i][2:]) - int(stats_static[i - 1][2:])

    for i in range(26):
        if i % 2 == 0:
            prev_time = int(stats_dynamic[i][2:])
        else:
            totals_dynamic += int(stats_dynamic[i][2:]) - int(stats_dynamic[i - 1][2:])

    print(f'static: {totals_static}')
    print(f'dynamic: {totals_dynamic}')
