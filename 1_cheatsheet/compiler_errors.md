# Compiler / linker / runtime errors

Read the FIRST error only; the rest are often consequences.

## g++ and linker errors

| Message | Meaning | Fix |
|---------|----------------------|-----|
| `undefined reference to 'Foo::bar()'` (linker, `ld returned 1 exit status`) | Declared but never defined, or its .cpp is not compiled/linked | Add the .cpp to `add_executable(...)` and re-run `cmake ..`; write the missing definition; check `Class::` prefix and exact signature (const!) match |
| `undefined reference to 'main'` | No main() in the compiled sources | Add main / list main.cpp in CMake |
| `undefined reference to 'cv::imread...'` / `'sqrt'` / Qt symbols | Library not linked | `target_link_libraries(target ${OpenCV_LIBS} ...)`, or `-lm`, `-lpthread` |
| `multiple definition of 'f()'` | Function body defined in a header included by several .cpp | Mark it `inline`, or move body to a .cpp |
| `expected unqualified-id before '.' token` | `.` used on a TYPE (`Maze.isFree(...)`); `.` needs an object | Use the existing object (here the static member `maze`). Not `Maze()`: that compiles but builds a new empty object |
| `no matching function for call to 'f(int, int)'` | No overload accepts these arg types/count | Read the "candidate:" lines: wrong arg count/type, missing `const`, missing include |
| `no matching function for call to 'Foo::Foo()'` | No default ctor and you declared `Foo f;` or a member without init-list | Provide args / add init list entry / `= default` |
| `passing 'const X' as 'this' argument discards qualifiers` | Calling a non-const method on a const object/reference (often a `const auto&` param) | Make the method `const` if it does not modify, or use a non-const variable |
| `use of deleted function 'Cell::Cell(const Cell&)'` | Copy of a non-copyable class (`auto c = cells[0];`, pass by value, vector of it growing) | Use a reference: `auto& c = ...`, `const auto&`, pass `const Cell&`, or pointers |
| `invalid use of non-static member function` / `invalid use of member function 'X::f()' (did you forget the '()' ?)` | `obj.size` / `cell.digit` written without calling it | Add `()`: `v.size()`, `cell.digit()` |
| `expected ';' before 'x'` | Missing `;` on the PREVIOUS line (often end of a class/struct: `};`) | Look one line above the reported line |
| `expected primary-expression before ')' token` | Type used where a value is expected, or stray comma/paren | Check call arguments |
| `'X' was not declared in this scope` | Typo, missing `#include`, missing `std::`, variable out of scope, or used before declaration | Add `#include <...>`, `std::`, check spelling (`neighboors`!) and scope |
| `'vector' in namespace 'std' does not name a template type` / `'string' is not a member of 'std'` | Missing include | `#include <vector>` / `<string>` |
| `'X' does not name a type` | Type unknown at that point: missing include, or circular include / missing forward declaration | Include the header, add include guards, forward-declare `class Cell;` |
| `'int Cell::digit_' is private within this context` | Private member accessed from outside the class | Use the public accessor `digit()`; `private` is per class (another Cell may access it) |
| `request for member 'x' in 'p', which is of pointer type 'Foo*' (maybe you meant to use '->' ?)` | `.` used on a pointer | Use `p->x`, or `(*p).x` |
| `base operand of '->' has non-pointer type 'Foo'` | `->` used on an object/reference | Use `.` |
| `no member named 'foo' in 'X'` (clang) / `'class X' has no member named 'foo'` (g++) | Typo, or no such method (e.g. `.len()`, `.remove()` on vector, `.length` w/o parens) | Check the header; use `.size()`, `erase` |
| `invalid operands to binary expression ('A' and 'B')` / `no match for 'operator==' (operand types are 'Node' and 'Node')` | Operator not defined for that type | Define `bool operator==(const Node&) const`; same for `<`, `<<`, `+` |
| `no match for 'operator<<' (operand types are 'std::ostream' and 'Foo')` | No `operator<<` for your class | Write `std::ostream& operator<<(std::ostream&, const Foo&)` or print members |
| `invalid conversion from 'const X*' to 'X*'` / `binding reference of type 'X&' to 'const X' discards qualifiers` | const mismatch | Add `const` to the receiving type, or copy |
| `cannot bind non-const lvalue reference of type 'T&' to an rvalue` | Passing a temporary to a `T&` parameter | Make the parameter `const T&` or pass a named variable |
| `conversion from 'double' to 'int' may change value` / `narrowing conversion` in `{}` | Brace-init refuses lossy conversion | `static_cast<int>(...)` |
| `control reaches end of non-void function` (warning) | Some path has no `return` -> UB, often crash | Add the final `return` (e.g. `return false;` after the loop) |
| `comparison of integer expressions of different signedness: 'int' and 'size_t'` (warning) | `int i < v.size()` | Use `size_t i`, range-for, or `static_cast<int>(v.size())` |
| `unused variable 'x'` / `unused parameter` (warning) | Harmless | Remove or `(void)x;` |
| `variable 'x' set but not used` / `may be used uninitialized` (warning) | The second is a likely real bug | Initialize: `int x = 0;` |
| `ISO C++ forbids declaration of 'x' with no type` | Missing type, or misspelled type | Check the type name/include |
| `invalid types 'int[int]' for array subscript` | `[]` on a non-array (e.g. 2-D index `cells[r][c]` on a 1-D `std::array`) | `cells[9*r + c]` |
| `class has virtual functions and accessible non-virtual destructor` (warning) | Base class without virtual dtor | `virtual ~Base() = default;` |
| `cannot allocate an object of abstract type` / `invalid new-expression of abstract class type` | Pure virtual not overridden in the derived class | Implement every `= 0` method with the same signature (use `override` to be told) |
| `'f' marked 'override', but does not override` | Signature differs from base (const, param type) | Match the base signature exactly |
| `template argument deduction/substitution failed` | Type lacks something the template needs (`operator<`, `neighboors()`...) | Read the "required from here" line and the first `error:` |
| `fatal error: foo.h: No such file or directory` | Wrong path, or include dir not in CMake | Check spelling, `"foo.h"` vs `<foo.h>`, `include_directories(...)` |
| `redefinition of 'class Foo'` | Header included twice without guard | Add `#ifndef/#define/#endif` or `#pragma once` |
| `a function-definition is not allowed here before '{'` | Missing `}` before this point | Count braces in the previous function |
| `ld: cannot find -lXXX` | Library not installed | Remove that link or install `libXXX-dev` (impossible offline: drop the optional dependency) |

## Segfault / crash causes (runtime)

`Segmentation fault (core dumped)`, `terminate called after throwing an instance of 'std::out_of_range'`, `free(): invalid pointer`, `double free`, `stack smashing detected`.

- Index out of range: `v[i]` with `i >= size()`, `v[-1]`, `cells[9*row+col]` out of bounds, `v.size() - 1` on empty vector (unsigned wrap), `back()/front()/pop_back()` on empty.
- Dangling pointer/reference: pointer to a local that went out of scope; reference or `Cell*` into a vector that then reallocated on `push_back`; reference to a temporary.
- Iterator invalidation: `erase` or `push_back` inside a range-for over the same vector; using `it` after `v.erase(it)` (use `it = v.erase(it)`).
- `erase(v.end())`: find returned `end()` and it was erased without checking `it != v.end()`.
- Dereferencing null / `end()`: `*min_element(...)` on an empty range, `map.find(k)->second` when k absent.
- Infinite recursion (stack overflow shows as `Segmentation fault`): missing base case in backtracking or minimax. Check the depth test (`if (depth == 0 || gameOver) return eval;`).
- Uninitialized pointer/variable: `Cell* p; p->digit();`
- Deleting twice, or mixing new[] with delete. Use smart pointers / vectors.
- Infinite loop (not a crash): unsigned `>= 0` loop, forgot `++`, A* with no closed set, `waitKey(0)` waiting for a key (click window, press a key).
- Unreachable goal / endless search: state not marked visited; neighbours not filtered by walls.

## CMake

```bash
rm -rf build && mkdir build && cd build && cmake .. && make -j4      # clean rebuild (when weird)
cmake -DCMAKE_BUILD_TYPE=Release ..    # fast
cmake -DCMAKE_BUILD_TYPE=Debug ..      # -g for gdb
make VERBOSE=1                         # show actual g++ commands
```
| Message | Meaning | Fix |
|---------|---------|-----|
| `Could not find a package configuration file provided by "OpenCV"` (or Qt5, Eigen3...) | The `-dev` package is not installed on this PC | Cannot install offline. If the dependency is only for display/GUI, make it optional: `find_package(OpenCV QUIET)` and wrap its use in `if(OpenCV_FOUND) ... endif()`, or drop that target. Check `CMakeLists.txt` for which targets need it |
| `CMake Error: The source directory ... does not appear to contain CMakeLists.txt` | cmake run in the wrong dir | `cmake ..` from `build/`, `cd` to project root first |
| `CMake Error: The current CMakeCache.txt directory ... is different` | build/ copied from another path/PC | `rm -rf build` |
| `Cannot find source file: foo.cpp` | Typo or file not in that folder | Fix the path in `add_executable` |
| New .cpp not compiled / `undefined reference` | cmake not re-run after adding file (or file missing from list) | Add to `add_executable`, run `cmake ..` again |
| `CMake Error at ... Policy` / `cmake_minimum_required` | Old/new CMake mismatch | Lower `cmake_minimum_required(VERSION 3.5)` |
| Compiles with warnings only but wrong result | Debug vs Release, uninitialized var | Add `-Wall -Wextra`, run with sanitizers |

Minimal template:
```cmake
cmake_minimum_required(VERSION 3.5)
project(exo CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
add_executable(exo main.cpp cell.cpp grid.cpp)
# debug build with sanitizers:
# set(CMAKE_CXX_FLAGS_DEBUG "-g -fsanitize=address,undefined")
```

## Debugging

### Sanitizers (first move for a crash)
```bash
g++ -std=c++17 -g -fsanitize=address,undefined -fno-omit-frame-pointer main.cpp cell.cpp -o main
./main
```
AddressSanitizer prints the exact line and stack trace of an out-of-bounds / use-after-free / double free. UBSan reports signed overflow, null deref, etc. In CMake: `cmake -DCMAKE_CXX_FLAGS="-g -fsanitize=address,undefined" ..`

### gdb
```bash
g++ -g -O0 main.cpp -o main      # -g needed, -O0 keeps variables readable
gdb ./main
(gdb) run                 # (r); run < input.txt; run arg1 arg2
(gdb) bt                  # backtrace after a crash, top = crash site
(gdb) frame 2             # (f 2)
(gdb) print x             # (p); p v.size(); p *ptr; p cells[3]; p/x n
(gdb) info locals
(gdb) break file.cpp:42   # (b); b Grid::solve
(gdb) continue            # (c)
(gdb) next                # (n) step over;  step (s) step into;  finish = run until return
(gdb) watch x             # stop when x changes
(gdb) up / down           # move between frames
(gdb) quit                # (q)
```
One-shot: `gdb -batch -ex run -ex bt ./main`.

### Qt Creator
- Pick **Debug** build mode (bottom-left kit selector) or breakpoints do not work.
- **F9**: toggle breakpoint on the current line.
- **F5**: start debugging (run to first breakpoint). Ctrl+R: run without debug. Ctrl+B: build.
- **F10**: step over; **F11**: step into; **Shift+F11**: step out; F5 again: continue; Shift+F5: stop.
- "Locals and Expressions" pane (right side) shows variables while paused.
- "Issues" pane (Alt+1): double-click an error to jump to the line.
- Clean build: Build > Clean All, or delete the build dir.

### Poor man's debugging
`std::cerr << "here " << x << std::endl;` and `assert(cond);` (`<cassert>`).

## Print debugging with dbg.h

```cpp
#include "dbg.h"          // copy 2_snippets/dbg.h next to your .cpp
dbg(x, v, cell.candidates(), m.size());
// stderr: [grid.cpp:42] x = 3 | v = {1, 2} | cell.candidates() = {4, 7} | m.size() = 2
```

- Prints names and values of numbers, strings, pairs, tuples and any container, nested ones included.
- `-DDBG_OFF` (or `#define DBG_OFF` before the include) silences every call without deleting them.
- Goes to stderr, so it does not mix with the program's normal output.

## Testing one method

Smallest state by hand, call the method, check, undo, check again. Full example: `2_snippets/method_test.cpp`.

```cpp
static int failures = 0;
#define CHECK(c) do { if (!(c)) { ++failures; std::cerr << "FAIL line " << __LINE__ << ": " #c "\n"; } } while (0)

a.set(2);    CHECK(!b.has(2));    // normal case
a.cancel();  CHECK(b.has(2));     // round trip back to the start
```

- `assert` does nothing in Release (`NDEBUG`); `CHECK` always runs.
- Test private methods through the public ones that call them (`prune` through `set`).
- Temporary: put it at the top of `main`, `return 0;` after it, delete before handing in.
