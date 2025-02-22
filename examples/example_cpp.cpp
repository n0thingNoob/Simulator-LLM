// example_cpp.cpp
#include "example.h"
#include <iostream>

Calculator::Calculator() : result(0) {}

void Calculator::add(int num) {
    result += num;
}

void Calculator::subtract(int num) {
    result -= num;
}

int Calculator::getResult() const {
    return result;
}

int main() {
    Calculator calc;
    calc.add(10);
    calc.subtract(5);
    
    std::cout << "Result: " << calc.getResult() << std::endl;
    return 0;
}