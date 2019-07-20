import sys

from CommandHelper import CommandHelper


if __name__ == "__main__":
    sim_secs_static = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats_static.txt'], './').splitlines()
    sim_secs_dynamic = CommandHelper.run_command_output(['awk', '/sim_sec/ {print $2}', f'stats_dynamic.txt'], './').splitlines()

    sim_insts_static = CommandHelper.run_command_output(['awk', '/sim_insts/ {print $2}', f'stats_static.txt'], './').splitlines()
    sim_insts_dynamic = CommandHelper.run_command_output(['awk', '/sim_insts/ {print $2}', f'stats_dynamic.txt'], './').splitlines()

    if len(sim_secs_static) != 27:
        print(f'static stats incorrect stats length {len(sim_secs_static)} {sim_secs_static}')
        sys.exit(-1)

    if len(sim_secs_dynamic) != 27:
        print(f'static stats incorrect stats length {len(sim_secs_dynamic)} {sim_secs_dynamic}')
        sys.exit(-1)

    total_sim_sec_static = 0
    total_sim_sec_dynamic = 0
    total_sim_insts_static = 0
    total_sim_insts_dynamic = 0
    prev_time = 0
    prev_insts = 0

    for i in range(26):
        if i % 2 == 0:
            prev_time = int(sim_secs_static[i][2:])
            prev_insts = int(sim_insts_static[i])
        else:
            #print(f'adding {int(stats_static[i][2:]):,} {int(stats_static[i-1][2:]):,} {int(stats_static[i][2:]) - int(stats_static[i - 1][2:]):,}')
            total_sim_sec_static += int(sim_secs_static[i][2:]) - int(sim_secs_static[i - 1][2:])
            total_sim_insts_static += int(sim_insts_static[i]) - int(sim_insts_static[i - 1])

    for i in range(26):
        if i % 2 == 0:
            prev_time = int(sim_secs_dynamic[i][2:])
            prev_insts = int(sim_insts_dynamic[i])
        else:
            #print(f'adding {int(stats_dynamic[i][2:]):,} {int(stats_dynamic[i - 1][2:]):,} {int(stats_dynamic[i][2:]) - int(stats_dynamic[i - 1][2:]):,}')
            total_sim_sec_dynamic += int(sim_secs_dynamic[i][2:]) - int(sim_secs_dynamic[i - 1][2:])
            total_sim_insts_dynamic += int(sim_insts_dynamic[i]) - int(sim_insts_dynamic[i - 1])

    print(f'static: {total_sim_sec_static} - {total_sim_insts_static}')
    print(f'dynamic: {total_sim_sec_dynamic} - {total_sim_insts_dynamic}')
