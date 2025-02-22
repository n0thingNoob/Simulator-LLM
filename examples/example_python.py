# example_python.py
class Shape:
    """A simple shape class for testing."""
    def __init__(self, name: str):
        self.name = name
        self._area = 0.0

    def calculate_area(self) -> float:
        """Calculate the area of the shape."""
        return self._area

    @property
    def area(self) -> float:
        return self._area

class Circle(Shape):
    def __init__(self, radius: float):
        super().__init__("circle")
        self.radius = radius
        self._calculate_area()

    def _calculate_area(self):
        import math
        self._area = math.pi * self.radius ** 2

def main():
    circle = Circle(5.0)
    print(f"Circle area: {circle.area:.2f}")

if __name__ == "__main__":
    main()