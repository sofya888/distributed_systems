#include <stdio.h>
#include "utils.h"

void print_result(const char* operation, double result) {
    printf("%s: %.2f\n", operation, result);
}

int get_user_input(int* a, int* b) {
    printf("Введите два числа: ");
    return scanf("%d %d", a, b);
}
