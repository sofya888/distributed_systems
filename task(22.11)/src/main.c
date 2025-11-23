#include <stdio.h>
#include "math.h"
#include "display.h"

int main(void){
    int ok=1;
    print_result("add", 3, 5, add(3,5), 1);
    print_result("sub", 7, 2, sub(7,2), 1);
    print_result("mul", 4, 6, mul(4,6), 1);
    int r = divide_safe(10, 0, &ok);
    print_result("div", 10, 0, r, ok);
    r = divide_safe(20, 4, &ok);
    print_result("div", 20, 4, r, ok);
    return 0;
}
