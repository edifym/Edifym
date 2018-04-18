//
// Created by Oipo on 4/18/2018.
//

#ifndef EDIFYMRUNNER_EXECUTABLE_TASK_H
#define EDIFYMRUNNER_EXECUTABLE_TASK_H

typedef void (*functionPtr)();

typedef struct task {
    char *name;
    functionPtr function;
    task* next_task;
} task;

#endif //EDIFYMRUNNER_EXECUTABLE_TASK_H
