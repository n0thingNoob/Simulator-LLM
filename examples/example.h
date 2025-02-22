// example.h
#ifndef EXAMPLE_H
#define EXAMPLE_H

class Calculator {
private:
    int result;

public:
    Calculator();
    void add(int num);
    void subtract(int num);
    int getResult() const;
};

#endif // EXAMPLE_H