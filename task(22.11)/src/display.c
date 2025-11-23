#include <stdio.h>
void print_result(const char* op, int a, int b, int res, int ok){
    if(!ok) { printf("Error: division by zero\n"); return; }
    printf("%s(%d, %d) = %d\n", op, a, b, res);
}
