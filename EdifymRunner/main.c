#include "gem5/m5ops.h"
#include "executable_task.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

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

char** str_split(char* a_str, const char a_delim)
{
    char** result    = 0;
    size_t count     = 0;
    char* tmp        = a_str;
    char* last_comma = 0;
    char delim[2];
    delim[0] = a_delim;
    delim[1] = 0;

    /* Count how many elements will be extracted. */
    while (*tmp)
    {
        if (a_delim == *tmp)
        {
            count++;
            last_comma = tmp;
        }
        tmp++;
    }

    /* Add space for trailing token. */
    count += last_comma < (a_str + strlen(a_str) - 1);

    /* Add space for terminating null string so caller
       knows where the list of returned strings ends. */
    count++;

    result = malloc(sizeof(char*) * count);

    if (result)
    {
        size_t idx  = 0;
        char* token = strtok(a_str, delim);

        while (token)
        {
            assert(idx < count);
            *(result + idx++) = strdup(token);
            token = strtok(0, delim);
        }
        assert(idx == count - 1);
        *(result + idx) = 0;
    }

    return result;
}

int main( int argc, char *argv[] ) {

    if(argc == 1) {
        printf("USAGE: EdifymRunner task_size task_names task1_args taskn_args\nEXAMPLE: EdifymRunner 2 autopilot;flybywire 2;2 1\n\nTASKS:\n");
        print_all_task_names(&tasks_to_execute);
        return -1;
    }

    char *end;

    long task_size = strtol(argv[1], &end, 10);

    if(task_size == 0) {
        return 0;
    }

    if(argc != 3 + task_size) {
        printf("USAGE: EdifymRunner task_size task_names task1_args taskn_args\nEXAMPLE: EdifymRunner 2 autopilot;flybywire 2;2 1\n\nTASKS:\n");
        print_all_task_names(&tasks_to_execute);
        return -1;
    }

    if(tasks_to_execute.function == NULL) {
        printf("Horrible disaster function is NULL for %s\n", tasks_to_execute.name);
        return -1;
    }

    char** tasks = str_split(argv[2], ';');

    if(!tasks) {
        printf("USAGE: EdifymRunner task_size task_names task1_args taskn_args\nEXAMPLE: EdifymRunner 2 autopilot;flybywire 2;2 1\n\nTASKS:\n");
        print_all_task_names(&tasks_to_execute);
        return -1;
    }

    tasks_to_execute.function();

    for (int i = 0; *(tasks + i); i++) {
        task* t = find_task_by_name(&tasks_to_execute, *(tasks + i));

        if(t == NULL) {
            printf("Horrible disaster trying to find task %s\n", *(tasks + i));
            print_all_task_names(&tasks_to_execute);
            return -1;
        }

        if(t->function == NULL) {
            printf("Horrible disaster function is NULL for task %s\n", t->name);
            return -1;
        }

        if(t->init != NULL) {
            char **task_args = str_split(argv[3 + i], ';');
            int count = 0;
            int args[6];

            for (int i = 0; *(task_args + i); i++) {
                args[i] = strtol(*(task_args + i), &end, 10);
                count++;
            }

            //printf("running with %i count %i %i %i %i %i %i\n", count, args[0], args[1], args[2], args[3], args[4], args[5]);

            t->init(count, args);

            for (int i = 0; *(task_args + i); i++) {
                free(*(task_args + i));
            }

            free(task_args);
        }

        m5_dump_stats(0, 0);
        t->function();
        m5_dump_stats(0, 0);
    }

    for (int i = 0; *(tasks + i); i++) {
        free(*(tasks + i));
    }

    free(tasks);

    return 0;
}
