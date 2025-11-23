#include "math.h"
int add(int a, int b){ return a + b; }
int sub(int a, int b){ return a - b; }
int mul(int a, int b){ return a * b; }
int divide_safe(int a, int b, int* ok){
    if(b==0){ if(ok) *ok = 0; return 0; }
    if(ok) *ok = 1;
    return a / b;
}
