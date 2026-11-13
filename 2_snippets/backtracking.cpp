// backtracking.cpp - generic recursive backtracking with the set / cancel (undo) pattern.
// Build: g++ -std=c++17 -Wall -Wextra -O2 backtracking.cpp -o backtracking
//
// Pattern (same as the sudoku exam: Cell::set / cancel, Grid::solveNextCell):
//   solve(state):
//     if state is complete          -> return true
//     pick the next decision point  (cell / row / variable)
//     for each candidate value:
//         state.set(decision, value)       // modify the state (and prune the others)
//         if solve(state) return true      // go deeper
//         state.cancel(decision, value)    // UNDO exactly what set() did
//     return false                         // dead end: caller will try its next value
//
// Golden rule: cancel() must restore the state EXACTLY as before set().
#include <algorithm>
#include <iostream>
#include <vector>

// Part 1: N-queens as a concrete problem. One queen per row, we choose a column.
class Queens
{
public:
    explicit Queens(int n)
        : n_(n), col_(static_cast<size_t>(n), -1),
          usedCol_(static_cast<size_t>(n), false),
          usedDiag1_(static_cast<size_t>(2 * n), false),
          usedDiag2_(static_cast<size_t>(2 * n), false) {}

    int size() const { return n_; }
    int columnOf(int row) const { return col_[static_cast<size_t>(row)]; }

    bool canSet(int row, int c) const
    {
        return !usedCol_[static_cast<size_t>(c)]
            && !usedDiag1_[static_cast<size_t>(row + c)]
            && !usedDiag2_[static_cast<size_t>(row - c + n_)];
    }

    void set(int row, int c)
    {
        col_[static_cast<size_t>(row)] = c;
        usedCol_[static_cast<size_t>(c)] = true;
        usedDiag1_[static_cast<size_t>(row + c)] = true;
        usedDiag2_[static_cast<size_t>(row - c + n_)] = true;
    }

    void cancel(int row, int c)
    {
        col_[static_cast<size_t>(row)] = -1;
        usedCol_[static_cast<size_t>(c)] = false;
        usedDiag1_[static_cast<size_t>(row + c)] = false;
        usedDiag2_[static_cast<size_t>(row - c + n_)] = false;
    }

    void print() const
    {
        for(int r = 0; r < n_; ++r)
        {
            for(int c = 0; c < n_; ++c)
                std::cout << (col_[static_cast<size_t>(r)] == c ? "Q " : ". ");
            std::cout << "\n";
        }
    }

private:
    int n_;
    std::vector<int> col_;
    std::vector<bool> usedCol_, usedDiag1_, usedDiag2_;
};

// First solution only.
// ADAPT: replace Queens by your state type, 'row' by your decision point and
// the loop over columns by the loop over candidate values.
bool solveFirst(Queens &q, int row)
{
    if(row == q.size())            // ADAPT: "state complete" test
        return true;

    for(int c = 0; c < q.size(); ++c)   // ADAPT: candidates for this decision
    {
        if(!q.canSet(row, c))
            continue;
        q.set(row, c);
        if(solveFirst(q, row + 1))
            return true;           // keep the state as is: it IS the solution
        q.cancel(row, c);
    }
    return false;
}

// All solutions: do not return on success, just count (and undo anyway).
int countAll(Queens &q, int row)
{
    if(row == q.size())
        return 1;
    int total = 0;
    for(int c = 0; c < q.size(); ++c)
    {
        if(!q.canSet(row, c))
            continue;
        q.set(row, c);
        total += countAll(q, row + 1);
        q.cancel(row, c);          // always cancel when searching for everything
    }
    return total;
}

// Part 2: generic skeleton (template) to copy. State must provide:
//   bool complete() const;
//   bool pickDecision(Decision &d) const;           // false if nothing left
//   std::vector<Value> candidates(const Decision&) const;
//   void set(const Decision&, const Value&);
//   void cancel(const Decision&, const Value&);
template<class State, class Decision, class Value>
bool backtrack(State &s)
{
    if(s.complete())
        return true;
    Decision d;
    if(!s.pickDecision(d))
        return false;
    for(const Value &v : s.candidates(d))
    {
        s.set(d, v);
        if(backtrack<State, Decision, Value>(s))
            return true;
        s.cancel(d, v);
    }
    return false;
}

// Part 3: "most constrained first" heuristic (sudoku exam: min_element).
// Instead of taking the next cell in order, pick the undecided cell with the
// FEWEST remaining candidates: failures are discovered much earlier.
//
//   std::vector<Cell*> todo = ...undecided cells...;
//   auto it = std::min_element(todo.begin(), todo.end(),
//       [](const Cell *a, const Cell *b){ return a->candidates() < b->candidates(); });
//   if (it == todo.end()) return true;   // nothing left -> solved
//   Cell *c = *it;
//   // ADAPT: try each candidate of *c with set / recurse / cancel.
//
// Tiny runnable version below: pick the row with fewest legal columns.
int legalCount(const Queens &q, int row)
{
    int k = 0;
    for(int c = 0; c < q.size(); ++c)
        if(q.canSet(row, c))
            ++k;
    return k;
}

bool solveMostConstrained(Queens &q, std::vector<int> &rowsLeft)
{
    if(rowsLeft.empty())
        return true;
    // ADAPT: comparator = "which decision is the most constrained"
    auto it = std::min_element(rowsLeft.begin(), rowsLeft.end(),
        [&q](int a, int b) { return legalCount(q, a) < legalCount(q, b); });
    const int row = *it;
    rowsLeft.erase(it);                      // remove from the todo list...
    for(int c = 0; c < q.size(); ++c)
    {
        if(!q.canSet(row, c))
            continue;
        q.set(row, c);
        if(solveMostConstrained(q, rowsLeft))
            return true;
        q.cancel(row, c);
    }
    rowsLeft.push_back(row);                 // ...and restore it when backtracking
    return false;
}

int main()
{
    Queens q(8);
    if(solveFirst(q, 0))
    {
        std::cout << "First solution of 8-queens:\n";
        q.print();
    }

    Queens q2(8);
    std::cout << "Number of solutions for 8 queens: " << countAll(q2, 0)
              << " (expected 92)\n";

    Queens q3(8);
    std::vector<int> rows;
    for(int r = 0; r < 8; ++r)
        rows.push_back(r);
    std::cout << "Most-constrained-first solve: "
              << (solveMostConstrained(q3, rows) ? "found" : "none") << "\n";
    return 0;
}
