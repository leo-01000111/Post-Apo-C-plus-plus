// method_test.cpp: test one method on its own before the whole program depends on it.
// Pattern: build the smallest state by hand -> call the method -> CHECK the state
//          -> undo -> CHECK you are back where you started (round trip).
// CHECK keeps working in Release builds; assert() does nothing when NDEBUG is defined.
#include <algorithm>
#include <iostream>
#include <vector>
#include "dbg.h"

static int failures = 0;
#define CHECK(cond)                                                                    \
    do {                                                                               \
        if (!(cond)) {                                                                 \
            ++failures;                                                                \
            std::cerr << "FAIL " << __FILE__ << ':' << __LINE__ << "  " #cond "\n";    \
        }                                                                              \
    } while (0)

// ADAPT: the class under test. Here a tiny sudoku-style cell: set() prunes the digit
// from its neighbours, cancel() restores it, with a counter because two cells can
// forbid the same digit for a shared neighbour.
struct Cell
{
    unsigned digit = 0;
    std::vector<unsigned> cand{1, 2, 3};
    unsigned pruned[4] = {0, 0, 0, 0};
    std::vector<Cell *> nb;

    bool has(unsigned d) const { return std::find(cand.begin(), cand.end(), d) != cand.end(); }
    void prune(unsigned d)
    {
        if (digit) return;
        if (pruned[d]++ == 0) cand.erase(std::find(cand.begin(), cand.end(), d));
    }
    void restore(unsigned d)
    {
        if (digit || pruned[d] == 0) return;
        if (--pruned[d] == 0) cand.push_back(d);
    }
    void set(unsigned d)
    {
        digit = d;
        for (Cell *n : nb) n->prune(d);
    }
    void cancel()
    {
        for (Cell *n : nb) n->restore(digit);
        digit = 0;
    }
};

int main()
{
    // ADAPT: smallest state that exercises the tricky case (b is a neighbour of a AND c)
    Cell a, b, c;
    a.nb = {&b};
    c.nb = {&b};

    a.set(2);
    CHECK(a.digit == 2);
    CHECK(!b.has(2));          // normal case: neighbour lost the digit
    CHECK(b.has(1));           // ...and nothing else

    c.set(2);
    a.cancel();
    CHECK(!b.has(2));          // still forbidden by c: the counter matters
    c.cancel();
    CHECK(b.has(2));           // round trip: back to the start
    CHECK(b.cand.size() == 3);

    dbg(a.digit, b.cand, b.pruned[2]);   // see the state when a CHECK fails

    if (failures) {
        std::cerr << failures << " check(s) failed\n";
        return 1;
    }
    std::cout << "all checks passed\n";
}
