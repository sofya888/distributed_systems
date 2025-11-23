#include <iostream>
#include "math_operations.h"
#include "string_operations.h"

void demonstrate_math_operations(){
    std::cout << "=== MATH ===\n";
    std::cout << "5 + 3 = " << add(5,3) << "\n";
    std::cout << "10 - 4 = " << subtract(10,4) << "\n";
    std::cout << "6 * 7 = " << multiply(6,7) << "\n";
    try {
        std::cout << "15/3 = " << divide(15,3) << "\n";
        std::cout << "10/0 = " << divide(10,0) << "\n";
    } catch(const std::exception& e){
        std::cout << "Error: " << e.what() << "\n";
    }
    for(int i=0;i<=5;++i) std::cout << i << "! = " << factorial(i) << "\n";
    ComplexNumber a(3,4), b(1,-2);
    std::cout << "a=" << a.to_string() << ", b=" << b.to_string() << "\n";
    std::cout << "a+b=" << a.add(b).to_string() << "\n";
    std::cout << "a*b=" << a.multiply(b).to_string() << "\n";
}

void demonstrate_string_operations(){
    std::cout << "\n=== STRINGS ===\n";
    char s[] = "Hello World";
    std::cout << "orig: " << s << "\n";
    reverse_string(s);
    std::cout << "rev:  " << s << "\n";
    std::cout << "radar -> " << (is_palindrome("radar") ? "pal" : "no") << "\n";
    std::cout << "hello -> " << (is_palindrome("hello") ? "pal" : "no") << "\n";

    StringProcessor p("Hello,World,Test,String");
    p.to_uppercase(); std::cout << "upper: " << p.get_string() << "\n";
    p.to_lowercase(); std::cout << "lower: " << p.get_string() << "\n";
    auto parts = p.split(',');
    std::cout << "parts: ";
    for(size_t i=0;i<parts.size();++i){
        if(i) std::cout << " | ";
        std::cout << parts[i];
    }
    std::cout << "\n";
    std::cout << "join: " << StringProcessor::join(parts, "::") << "\n";
}

int main(){
    try{
        demonstrate_math_operations();
        demonstrate_string_operations();
    } catch(const std::exception& e){
        std::cerr << "Unhandled: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
