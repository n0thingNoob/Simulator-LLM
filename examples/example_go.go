// example_go.go
package main

import (
    "fmt"
)

type Person struct {
    Name string
    Age  int
}

func (p *Person) Birthday() {
    p.Age++
}

func (p Person) Greet() string {
    return fmt.Sprintf("Hello, my name is %s and I am %d years old", p.Name, p.Age)
}

func main() {
    person := Person{
        Name: "Alice",
        Age:  25,
    }

    fmt.Println(person.Greet())
    person.Birthday()
    fmt.Println(person.Greet())
}