# C++17 cheat-sheet (ARPRO)

Compile: `g++ -std=c++17 -Wall -Wextra -g main.cpp -o main`

## Header / source split

```cpp
// cell.h
#ifndef CELL_H            // include guard (or: #pragma once)
#define CELL_H
#include <vector>
class Cell {
public:
    Cell(int x, int y);
    int digit() const;
private:
    int digit_ = 0;
};
#endif
```
```cpp
// cell.cpp
#include "cell.h"
Cell::Cell(int x, int y) : digit_(0) {}
int Cell::digit() const { return digit_; }
```
- Declarations in .h, definitions in .cpp (`Class::method`). Templates: definitions must stay in the .h.
- Every .cpp must be listed in CMake `add_executable` (or a glob) or you get "undefined reference".
- `#include "mine.h"` for your files, `<vector>` for the standard library.
- Never `using namespace std;` in a header.
- `uint` is a Linux/glibc typedef (`unsigned int`). On other platforms write `unsigned int`.

## Classes

```cpp
class Point {
public:
    Point() = default;
    Point(int x, int y) : x_(x), y_(y) {}       // init list (members init in DECLARATION order)
    explicit Point(int v) : x_(v), y_(v) {}     // no implicit int -> Point
    Point(const Point&) = default;
    Point& operator=(const Point&) = default;
    virtual ~Point() = default;                 // virtual dtor if used polymorphically

    int x() const { return x_; }                // const method: cannot modify members
    void setX(int x) { x_ = x; }
    static int count() { return count_; }       // static: no this, call Point::count()
    friend std::ostream& operator<<(std::ostream&, const Point&);  // friend: can see privates
private:
    int x_ = 0, y_ = 0;                         // default member init
    static inline int count_ = 0;               // C++17: static member defined in class
};
```
- `struct` is `class` with public default.
- `obj.x()` for objects/references, `ptr->x()` (= `(*ptr).x()`) for pointers.
- `private` is per CLASS, not per object: a `Cell` can touch another `Cell`'s privates.
- Initialization list is required for const members, reference members and base classes without default ctor.
- Delete copying: `Cell(const Cell&) = delete;` -> then use `auto&` / pointers, never `auto`.
- `this` is a pointer: `this->x_`, `return *this;`.
- Static member function vs member function: static has no `this`, cannot touch non-static members.

## Inheritance, virtual

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;            // pure virtual => abstract class
    virtual void print() const { std::cout << "shape\n"; }
};
class Circle : public Shape {
public:
    Circle(double r) : Shape(), r_(r) {}        // base ctor in init list
    double area() const override { return 3.14159 * r_ * r_; }   // override: compiler checks signature
private:
    double r_;
};
Shape* s = new Circle(2);   s->area();  delete s;      // virtual dispatch through pointer/reference
std::vector<std::unique_ptr<Shape>> v;  v.push_back(std::make_unique<Circle>(1.0));
```
- Polymorphism only through pointers/references, not by value (slicing).
- `class Node : public ecn::Point`: Node gets Point's public members (`x`, `y`).
- Call the base version: `Shape::print();`
- `protected`: visible to derived classes, hidden from outside.
- `final` stops further overriding.

## References, pointers, smart pointers

```cpp
int a = 5;
int& r = a;        // reference: alias, must be initialized, cannot be reseated
int* p = &a;       // pointer: *p is the value; can be nullptr
const int* cp;     // pointer to const int (cannot change *cp)
int* const pc = &a;// const pointer (cannot change pc)
void f(int& out);        // modifies caller's variable
void g(const Big& in);   // read-only, no copy (preferred for big objects)
void h(Big b);           // copy
```
```cpp
#include <memory>
auto u = std::make_unique<Cell>(1, 2);   // sole owner, auto-deleted, not copyable
u->digit();   (*u).digit();   u.get();   // u.get() = raw pointer
auto u2 = std::move(u);                  // transfer ownership (u is now null)
auto s = std::make_shared<Cell>(1, 2);   // shared ownership, ref-counted
auto s2 = s;  s.use_count();             // 2
```
- Raw `new` needs `delete`; arrays `new int[n]` need `delete[]`. Prefer vector / smart pointers.
- Never return a reference/pointer to a local variable (dangling).
- Pointer to element of a vector dies on `push_back` realloc.
- `nullptr` not `NULL`/`0`.

## const correctness

```cpp
int Cell::digit() const;                   // const method: callable on const objects
const std::vector<int>& cands() const;     // read-only view, no copy
for (const auto& c : cells) c.digit();     // const object => only const methods allowed
```
"passing const X as this discards qualifiers" = non-const method called on a const object. Mark the method `const` (if it does not modify) or drop `const` from the variable.

## Operator overloading

```cpp
struct P {
    int x, y;
    bool operator==(const P& o) const { return x == o.x && y == o.y; }
    bool operator!=(const P& o) const { return !(*this == o); }
    bool operator<(const P& o) const { return std::tie(x, y) < std::tie(o.x, o.y); } // for set/map/sort
    P operator+(const P& o) const { return {x + o.x, y + o.y}; }
    P& operator+=(const P& o) { x += o.x; y += o.y; return *this; }
    int& operator[](size_t i) { return i == 0 ? x : y; }              // read/write
    const int& operator[](size_t i) const { return i == 0 ? x : y; }  // const version
};
std::ostream& operator<<(std::ostream& os, const P& p) { return os << '(' << p.x << ',' << p.y << ')'; }
```
- `std::tie` needs `<tuple>`. `std::set<P>` / `std::map<P,..>` / `std::sort` need `operator<` (or a comparator).
- `unordered_set<P>` needs `operator==` AND a hash.
- `operator<<` is a free function (or friend), first arg `std::ostream&`, return the stream.

## Lambdas

```cpp
auto sq = [](int x) { return x * x; };
int k = 3;
auto byVal  = [k](int x) { return x + k; };     // copy of k
auto byRef  = [&k](int x) { k += x; };          // reference to k
auto allRef = [&](int x) { k += x; };           // everything by reference
auto allVal = [=](int x) { return x + k; };     // everything by copy (read-only unless mutable)
auto mut    = [k](int x) mutable { k += x; return k; };
// inside a member function:
auto m = [this](int x) { return x + member_; }; // captures the this pointer
auto cmp = [](const Cell& a, const Cell& b) { return a.candidates().size() < b.candidates().size(); };
std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });
auto r = [](int a) -> double { return a / 2.0; };  // explicit return type
```
- Do not capture by reference something that dies before the lambda runs.
- Generic lambda: `[](auto a, auto b) { return a < b; }`.

## auto, structured bindings, range-for

```cpp
auto x = 5;            // int
auto d = 5.0;          // double
auto s = std::string("a");
auto  c = cells[0];    // COPY (fails if non-copyable)
auto& c = cells[0];    // reference, no copy
const auto& c = cells[0];

std::map<std::string,int> m;
for (const auto& [key, val] : m) std::cout << key << val;   // structured binding
auto [it, inserted] = m.insert({"a", 1});
std::pair<int,int> pr{1,2};  auto [a, b] = pr;

for (int v : vec) {}            // copy of each element (modifying v changes nothing)
for (int& v : vec) v *= 2;      // modify in place
for (const auto& v : vec) {}    // read-only, no copy (default choice for big types)
for (auto nb : cell.neighboors()) // fine when elements are pointers (copying a pointer is cheap)
```
- `auto` drops `&` and `const`: use `auto&` / `const auto&` explicitly.

## Templates

```cpp
template <typename T>
T maxOf(T a, T b) { return a < b ? b : a; }
maxOf(3, 4);  maxOf<double>(3, 4.5);

template <typename T, int N = 3>
class Stack {
public:
    void push(const T& t) { data_.push_back(t); }
    T pop() { T t = data_.back(); data_.pop_back(); return t; }
    bool empty() const { return data_.empty(); }
private:
    std::vector<T> data_;
};
Stack<int> s;  s.push(1);
```
Generic A*: `template <class Node> ... AStar(Node start, Node goal)` calls `node.neighboors()`, `node.distToPrevious()`, `node == goal`, `node.h(goal)`, `node.print(next)`. Node must provide exactly those.

```cpp
// requires a member `std::vector<Node> neighboors() const`
template <class N>
void expand(const N& n) { for (const auto& nb : n.neighboors()) { /* ... */ } }
```
- Template code lives entirely in headers.
- Error messages are long: read the first line and the "required from here" line.

## std::function

```cpp
#include <functional>
std::function<int(int,int)> op = [](int a, int b) { return a + b; };
op = std::plus<int>();                 // any callable
int apply(std::function<int(int)> f, int x) { return f(x); }
std::function<double(const Node&)> heuristic;   // stored callback
```
Slower than a template parameter / `auto`, but storable in members and containers.

## enums

```cpp
enum class Dir { Up, Down, Left, Right };   // scoped: Dir::Up, no implicit int
Dir d = Dir::Left;
int i = static_cast<int>(d);
Dir e = static_cast<Dir>(2);
switch (d) { case Dir::Up: break; default: break; }
enum Color { Red, Green };                  // old style: Red is an int, pollutes scope
```

## Casting

```cpp
double d = static_cast<double>(a) / b;
int i = static_cast<int>(3.9);              // 3 (truncates)
size_t n = static_cast<size_t>(i);
// reinterpret_cast (bit reinterpretation), const_cast (remove const), dynamic_cast (checked downcast, needs virtual):
if (auto* c = dynamic_cast<Circle*>(shapePtr)) { /* it is a Circle */ }
```
Avoid C casts `(int)x`: they hide bugs.

## Arithmetic pitfalls

```cpp
5 / 2        // 2   (integer division truncates toward zero)
5 / 2.0      // 2.5
-5 / 2       // -2
5 % 3        // 2
-5 % 3       // -2   (sign follows the dividend!)  positive modulo: ((a % n) + n) % n
double avg = sum / n;            // WRONG if both int: use static_cast<double>(sum) / n
1 / 3 * 3.0  // 0   (1/3 is integer 0)
```
```cpp
unsigned int a = 3, b = 5;
a - b;                     // 4294967294, NOT -2 (wraps around)
std::vector<int> v;
v.size() - 1;              // huge number when v is empty!
for (size_t i = v.size() - 1; i >= 0; --i) {}   // INFINITE LOOP: size_t >= 0 is always true
for (size_t i = v.size(); i-- > 0; ) {}         // correct reverse loop
for (int i = 0; i < (int)v.size(); ++i) {}      // or cast to avoid signed/unsigned warning
if (i < v.size())          // warning "comparison of signed and unsigned" if i is int
```
- `abs(int)` vs `std::abs(double)`: include `<cmath>`/`<cstdlib>` and call `std::abs`. Plain `abs(-2.5)` may truncate to int.
- Float equality: compare with epsilon `std::abs(a-b) < 1e-9`.
- `int` overflow around 2.1e9: use `long long` for big sums / factorials.
- `char` arithmetic: `'a' + 1` is int; `c - '0'` converts a digit char to int.
- `=` vs `==` in `if`.
- Uninitialized locals (`int x;`) hold garbage.

## Misc syntax

```cpp
const int N = 9;  constexpr int M = 3 * N;
using Grid = std::array<std::array<int,9>,9>;     // type alias
std::array<Cell, 81> cells;  cells[9*row + col];  // 1-D grid indexing
int a[3] = {1,2,3};
if (auto it = m.find(k); it != m.end()) { }       // C++17 if with initializer
std::optional<int> o = std::nullopt;  if (o) *o;  // #include <optional>
std::swap(a, b);
cond ? x : y
std::cout << "x=" << x << '\n';   std::cerr << "err\n";
std::cin >> n;   std::getline(std::cin, line);
```
