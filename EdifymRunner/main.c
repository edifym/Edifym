#include "gem5/m5ops.h"
#include "executable_task.h"
#include <string.h>
#include <stdio.h>

extern task tasks_to_execute;

task* find_task_by_name(task* t, char const *name) {
    while(t != NULL) {
        printf("checking for %s in task %s\n", name, t->name);
        if (strcmp(t->name, name) == 0) {
            return t;
        }
        t = t->next_task;
    }

    return NULL;
}

int main( void ) {
    functionPtr function;
    char *ordered_task_names[TASK_SIZE] = TASKS;
    printf("Started with TASK_SIZE %i\n", TASK_SIZE);

    for (int i = 0; i < TASK_SIZE; i++) {
        task* t = find_task_by_name(&tasks_to_execute, ordered_task_names[i]);

        if(t == NULL) {
            printf("Horrible disaster\n");
            return -1;
        }

        function = t->function;

        m5_reset_stats(0, 0);
        function();
        m5_dump_stats(0, 0);
    }
    return 0;
}
