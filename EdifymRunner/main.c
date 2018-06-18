#include "gem5/m5ops.h"
#include "executable_task.h"
#include <string.h>
#include <stdio.h>
#include <sys/time.h>

extern task tasks_to_execute;
#define ENABLE_TRACE 0

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

int main( void ) {
    functionPtr function;
    char *ordered_task_names[TASK_SIZE] = TASKS;
    printf("Started with TASK_SIZE %i\n", TASK_SIZE);

    for (int i = 0; i < TASK_SIZE; i++) {
        task* t = find_task_by_name(&tasks_to_execute, ordered_task_names[i]);

        if(t == NULL) {
            printf("Horrible disaster trying to find task %s\n", ordered_task_names[i]);
            print_all_task_names(&tasks_to_execute);
            return -1;
        }

        if(t->init == NULL) {
            printf("Horrible disaster trying to init for task %s\n", t->name);
            return -1;
        }
        t->init(1, 100);
        print_time();
        m5_reset_stats(0, 0);
        t->function();
        m5_dump_stats(0, 0);
        print_time();
    }
    return 0;
}
