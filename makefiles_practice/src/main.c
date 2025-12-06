#include <stdio.h>
#include "calculator.h"
#include "utils.h"

int main() {
    int a, b;

    printf("=== Калькулятор ===\n");

    if (get_user_input(&a, &b) != 2) {
        printf("Ошибка ввода!\n");
        return 1;
    }

    print_result("Сложение", add(a, b));
    print_result("Вычитание", subtract(a, b));
    print_result("Умножение", multiply(a, b));
    print_result("Деление", divide(a, b));

    return 0;
}
