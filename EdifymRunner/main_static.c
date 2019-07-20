#include "gem5/m5ops.h"
#include "executable_task.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <assert.h>

extern task tasks_to_execute;
#define ENABLE_TRACE 0

#define EXECUTE_TASK(task, valcount, valone, valtwo, valthree, valfour, valfive, valsix) t = find_task_by_name(&tasks_to_execute, task); \
    if(t == NULL) { printf("Horrible disaster trying to find task %s\n", task); return -1; } \
    if(t->init != NULL) { \
        values[0] = valone; values[1] = valtwo; values[2] = valthree; values[3] = valfour; values[4] = valfive; values[5] = valsix; \
        t->init(valcount, values); } \
    m5_dump_stats(0, 0); t->function(); m5_dump_stats(0, 0);

task* find_task_by_name(task* t, char const *name) {
    while(t != NULL) {
#if defined(ENABLE_TRACE) && ENABLE_TRACE > 0
        printf("checking for %s in task %s\n", name, t->name);
#endif
        if (strcmp(t->name, name) == 0) {
            return t;
        }
        t = t->next_task;
    }

    return NULL;
}

void print_all_task_names(task* t) {
    while(t != NULL) {
        printf("%s\n", t->name);
        t = t->next_task;
    }
}

void print_time() {
  struct timeval tv;
  int ret = gettimeofday(&tv, NULL);
  printf("time: %i %li %li\n", ret, tv.tv_sec, tv.tv_usec);
}

int main( int argc, char *argv[] ) {

    if(tasks_to_execute.function == NULL) {
        printf("Horrible disaster function is NULL for %s\n", tasks_to_execute.name);
        return -1;
    }

    tasks_to_execute.function();

    task* t = NULL;
    int values[6];

    EXECUTE_TASK("test_ppm_task", 4, 1, 0, 1, 1, 0, 0)
    EXECUTE_TASK("servo_transmit", 1, 0, 0, 0, 0, 0, 0)
    EXECUTE_TASK("send_data_to_autopilot_task", 4, 0, 1, 1, 1, 0, 0)
    EXECUTE_TASK("check_mega128_values_task", 4, 0, 1, 0, 1, 0, 0)
    EXECUTE_TASK("check_failsafe_task", 1, 0, 0, 0, 0, 0, 0)
    EXECUTE_TASK("stabilisation_task", 1, 1, 0, 0, 0, 0, 0)
    EXECUTE_TASK("reporting_task", 1, 0, 0, 0, 0, 0, 0)
    EXECUTE_TASK("receive_gps_data_task", 6, 0, 3, 0, 0, 0, 6)
    EXECUTE_TASK("radio_control_task", 5, 1, 4, 1, 1, 0, 0)
    EXECUTE_TASK("navigation_task", 2, 0, 3, 0, 0, 0, 0)
    EXECUTE_TASK("link_fbw_send", 1, 1, 0, 0, 0, 0, 0)
    EXECUTE_TASK("climb_control_task", 5, 0, 1, 7, 6, 1, 0)
    EXECUTE_TASK("altitude_control_task", 1, 1, 0, 0, 0, 0, 0)

    return 0;
}
