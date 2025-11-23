#ifndef MATH_OPERATIONS_H
#define MATH_OPERATIONS_H

#include <string>

int add(int a, int b);
int subtract(int a, int b);
int multiply(int a, int b);
double divide(double a, double b);
unsigned long long factorial(int n);
bool is_prime(int number);

class ComplexNumber {
private:
    double real_part;
    double imag_part;
public:
    ComplexNumber(double real = 0.0, double imag = 0.0);
    double get_real() const;
    double get_imag() const;
    ComplexNumber add(const ComplexNumber& other) const;
    ComplexNumber multiply(const ComplexNumber& other) const;
    std::string to_string() const;
};

#endif // MATH_OPERATIONS_H
