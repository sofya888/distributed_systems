#include "math_operations.h"
#include <stdexcept>
#include <sstream>
#include <cmath>

int add(int a, int b){ return a + b; }
int subtract(int a, int b){ return a - b; }
int multiply(int a, int b){ return a * b; }

double divide(double a, double b){
    if(b == 0.0) throw std::runtime_error("Division by zero!");
    return a / b;
}

unsigned long long factorial(int n){
    if(n < 0) throw std::invalid_argument("Factorial is not defined for negative numbers");
    unsigned long long res = 1;
    for(int i=2;i<=n;++i) res *= i;
    return res;
}

bool is_prime(int number){
    if(number <= 1) return false;
    if(number == 2) return true;
    if(number % 2 == 0) return false;
    for(int i=3; i*i<=number; i+=2)
        if(number % i == 0) return false;
    return true;
}

ComplexNumber::ComplexNumber(double r, double i): real_part(r), imag_part(i) {}
double ComplexNumber::get_real() const { return real_part; }
double ComplexNumber::get_imag() const { return imag_part; }

ComplexNumber ComplexNumber::add(const ComplexNumber& o) const {
    return ComplexNumber(real_part + o.real_part, imag_part + o.imag_part);
}
ComplexNumber ComplexNumber::multiply(const ComplexNumber& o) const {
    double nr = real_part * o.real_part - imag_part * o.imag_part;
    double ni = real_part * o.imag_part + imag_part * o.real_part;
    return ComplexNumber(nr, ni);
}
std::string ComplexNumber::to_string() const {
    std::ostringstream oss;
    oss << real_part;
    if (imag_part >= 0) oss << " + " << imag_part << "i";
    else oss << " - " << -imag_part << "i";
    return oss.str();
}
