// astar.cpp - self-contained generic A* (template) + 8-puzzle demo.
// Build: g++ -std=c++17 -Wall -Wextra -O2 astar.cpp -o astar
//
// Professor's Node interface (maze/include/a_star.h, note the spelling "neighboors"):
//     std::vector<Node> neighboors() const;     // successors of this state
//     int  distToPrevious() const;              // cost of the step that led here (1 on grids)
//     bool operator==(const Node &other) const; // same state?
//     double h(const Node &goal) const;         // admissible heuristic (never overestimates)
//
// Two flavours:
//   astar(start, goal)             needs ONLY the interface above (linear lookup, simple, slow
//                                  when many nodes are generated)
//   astarKeyed(start, goal, key)   same + a key function Node -> std::string (or int, pair...)
//                                  so duplicate detection is O(log n). Use for puzzles.
//
// ecn::Astar plug-in: search "USE_ECN_ASTAR".
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdlib>
#include <iostream>
#include <map>
#include <queue>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

namespace astar_snip
{

struct Stats
{
    size_t expanded = 0;   // nodes popped and expanded
    size_t generated = 0;  // nodes created by neighboors()
};

// Open-set entry. f = g + h.
struct OpenEntry
{
    double f;
    int g;
    size_t idx;   // index into the "nodes" vector
};

// priority_queue is a max-heap, so "less" means "worse": larger f is worse;
// on equal f prefer the deeper node (larger g), it usually finds the goal faster.
struct OpenWorse
{
    bool operator()(const OpenEntry &a, const OpenEntry &b) const
    {
        if(a.f != b.f)
            return a.f > b.f;
        return a.g < b.g;
    }
};

// Duplicate lookup #1: only needs operator== (linear search).
template<class Node>
struct LinearIndex
{
    static constexpr size_t npos = static_cast<size_t>(-1);
    size_t find(const std::vector<Node> &nodes, const Node &n) const
    {
        for(size_t i = 0; i < nodes.size(); ++i)
            if(nodes[i] == n)          // ADAPT: uses Node::operator==
                return i;
        return npos;
    }
    void add(const Node &, size_t) {}
};

// Duplicate lookup #2: ordered map from a key to the node index.
template<class Node, class KeyFn>
struct MapIndex
{
    using Key = std::decay_t<decltype(std::declval<KeyFn>()(std::declval<Node>()))>;
    static constexpr size_t npos = static_cast<size_t>(-1);
    explicit MapIndex(KeyFn k) : key(std::move(k)) {}
    size_t find(const std::vector<Node> &, const Node &n) const
    {
        auto it = table.find(key(n));
        return it == table.end() ? npos : it->second;
    }
    void add(const Node &n, size_t idx) { table[key(n)] = idx; }
    KeyFn key;
    std::map<Key, size_t> table;
};

// Index = LinearIndex or MapIndex.
// Returns the path start..goal (empty vector if no solution).
template<class Node, class Index>
std::vector<Node> core(const Node &start, const Node &goal, Index &index, Stats *stats)
{
    const size_t npos = static_cast<size_t>(-1);
    std::vector<Node> nodes;           // owner of every state ever created
    std::vector<size_t> parent;        // parent[i] = index of the node we came from
    std::vector<int> gCost;            // best known cost from start to nodes[i]
    std::vector<double> hCost;         // cached heuristic (computed once per node)
    std::vector<char> closed;          // 1 = already expanded with its best g
    std::priority_queue<OpenEntry, std::vector<OpenEntry>, OpenWorse> open;

    nodes.push_back(start);
    parent.push_back(npos);
    gCost.push_back(0);
    hCost.push_back(start.h(goal));
    closed.push_back(0);
    index.add(start, 0);
    open.push(OpenEntry{hCost[0], 0, 0});

    while(!open.empty())
    {
        const OpenEntry cur = open.top();
        open.pop();
        // lazy deletion: skip stale entries (a cheaper path was found meanwhile)
        if(cur.g > gCost[cur.idx] || closed[cur.idx])
            continue;
        closed[cur.idx] = 1;
        if(stats)
            ++stats->expanded;

        if(nodes[cur.idx] == goal)     // goal test when POPPED -> optimal path
        {
            std::vector<Node> path;
            for(size_t i = cur.idx; i != npos; i = parent[i])
                path.push_back(nodes[i]);
            std::reverse(path.begin(), path.end());
            return path;
        }

        // copy: 'nodes' may reallocate while we push below
        const Node here = nodes[cur.idx];
        for(const Node &nb : here.neighboors())   // ADAPT: neighboors()
        {
            if(stats)
                ++stats->generated;
            const int ng = cur.g + nb.distToPrevious();   // ADAPT: distToPrevious()
            const size_t found = index.find(nodes, nb);
            if(found == npos)
            {
                nodes.push_back(nb);
                parent.push_back(cur.idx);
                gCost.push_back(ng);
                hCost.push_back(nb.h(goal));   // ADAPT: h(goal)
                closed.push_back(0);
                index.add(nb, nodes.size() - 1);
                open.push(OpenEntry{ng + hCost.back(), ng, nodes.size() - 1});
            }
            else if(ng < gCost[found])        // shorter way to a known node
            {
                gCost[found] = ng;
                parent[found] = cur.idx;
                closed[found] = 0;            // re-open (needed if h is inconsistent)
                open.push(OpenEntry{ng + hCost[found], ng, found});
            }
        }
    }
    return {};
}

} // namespace astar_snip

// Public API: copy these two functions (plus the namespace above)

// Only requires the professor's Node interface.
template<class Node>
std::vector<Node> astar(const Node &start, const Node &goal,
                        astar_snip::Stats *stats = nullptr)
{
    astar_snip::LinearIndex<Node> index;
    return astar_snip::core(start, goal, index, stats);
}

// Same, with a key function for fast duplicate detection.
// ADAPT: key must be identical for equal states, e.g. [](const Puzzle &p){ return p.str(); }
template<class Node, class KeyFn>
std::vector<Node> astarKeyed(const Node &start, const Node &goal, KeyFn key,
                             astar_snip::Stats *stats = nullptr)
{
    astar_snip::MapIndex<Node, KeyFn> index(key);
    return astar_snip::core(start, goal, index, stats);
}

// Demo node: 8-puzzle (3x3 sliding tiles). 0 is the blank.
// ADAPT: replace this whole struct by your own state (keep the 4 interface methods).
struct Puzzle
{
    std::array<int, 9> t;

    explicit Puzzle(const std::array<int, 9> &tiles) : t(tiles) {}

    bool operator==(const Puzzle &o) const { return t == o.t; }

    int distToPrevious() const { return 1; }

    // Manhattan distance of every tile (blank excluded) to its place in 'goal'.
    double h(const Puzzle &goal) const
    {
        int total = 0;
        for(int i = 0; i < 9; ++i)
        {
            if(t[static_cast<size_t>(i)] == 0)
                continue;
            int gi = 0;
            for(int j = 0; j < 9; ++j)
                if(goal.t[static_cast<size_t>(j)] == t[static_cast<size_t>(i)])
                    gi = j;
            total += std::abs(i / 3 - gi / 3) + std::abs(i % 3 - gi % 3);
        }
        return static_cast<double>(total);
    }

    std::vector<Puzzle> neighboors() const
    {
        std::vector<Puzzle> res;
        int z = 0;
        for(int i = 0; i < 9; ++i)
            if(t[static_cast<size_t>(i)] == 0)
                z = i;
        const int r = z / 3, c = z % 3;
        const int dr[4] = {-1, 1, 0, 0};
        const int dc[4] = {0, 0, -1, 1};
        for(int k = 0; k < 4; ++k)
        {
            const int nr = r + dr[k], nc = c + dc[k];
            if(nr < 0 || nr > 2 || nc < 0 || nc > 2)
                continue;
            Puzzle n(*this);
            std::swap(n.t[static_cast<size_t>(z)], n.t[static_cast<size_t>(nr * 3 + nc)]);
            res.push_back(n);
        }
        return res;
    }

    // Move the blank in direction k (0 up, 1 down, 2 left, 3 right) if legal.
    void slide(int k)
    {
        int z = 0;
        for(int i = 0; i < 9; ++i)
            if(t[static_cast<size_t>(i)] == 0)
                z = i;
        const int dr[4] = {-1, 1, 0, 0};
        const int dc[4] = {0, 0, -1, 1};
        const int nr = z / 3 + dr[k], nc = z % 3 + dc[k];
        if(nr < 0 || nr > 2 || nc < 0 || nc > 2)
            return;
        std::swap(t[static_cast<size_t>(z)], t[static_cast<size_t>(nr * 3 + nc)]);
    }

    std::string str() const
    {
        std::string s;
        for(int i = 0; i < 9; ++i)
        {
            s += static_cast<char>('0' + t[static_cast<size_t>(i)]);
            if(i % 3 == 2 && i != 8)
                s += '/';
        }
        return s;
    }

    // Number of inversions (pairs out of order, blank ignored).
    int inversions() const
    {
        int inv = 0;
        for(int i = 0; i < 9; ++i)
            for(int j = i + 1; j < 9; ++j)
            {
                const int a = t[static_cast<size_t>(i)], b = t[static_cast<size_t>(j)];
                if(a != 0 && b != 0 && a > b)
                    ++inv;
            }
        return inv;
    }
};

// Solvability on an odd-width board: start can reach goal iff the inversion parities match.
// 15-puzzle (width 4, even): solvable iff (inversions + row of the blank counted from the
// bottom, 1-based) has the same parity as for the goal. Only this formula changes.
bool solvable(const Puzzle &start, const Puzzle &goal)
{
    return (start.inversions() % 2) == (goal.inversions() % 2);
}

size_t moves(const std::vector<Puzzle> &path)
{
    return path.empty() ? size_t(0) : path.size() - 1;
}

// Plugging a Node into the course's own ecn::Astar  (maze/include/a_star.h)
// Call:   std::vector<Node> path = ecn::Astar(start, goal);   // namespace ecn, header <a_star.h>
// It prints stats ("nodes created, evaluated, shortcuts") and the time, returns the path.
//
// Requirements on Node, as actually used by a_star.h (differences with the interface above):
//   * copy/move constructible (the tree stores copies in a std::vector<Node>)
//   * bool operator==(const Node&) const
//   * int distToPrevious() const
//   * std::vector<Node> neighboors() const
//   * int h(const Node &goal) const          <-- returns INT here (it is stored as int)
//   * void print(const Node &next) const     <-- REQUIRED: fullPathTo() calls
//                                                 path[i-1].print(path[i]) for each step
// ecn::Astar does not need a key function (it searches its queue linearly: slow on big
// state spaces, fine for mazes). Compile with the course header on the include path:
//   g++ -std=c++17 -DUSE_ECN_ASTAR -I<course>/maze/include astar.cpp
// The wrapper below is compiled only with -DUSE_ECN_ASTAR, so this file still builds alone.
#ifdef USE_ECN_ASTAR
#include <a_star.h>

struct EcnPuzzle
{
    Puzzle p;
    explicit EcnPuzzle(const Puzzle &q) : p(q) {}
    bool operator==(const EcnPuzzle &o) const { return p == o.p; }
    int distToPrevious() const { return 1; }
    int h(const EcnPuzzle &goal) const { return static_cast<int>(p.h(goal.p)); }
    std::vector<EcnPuzzle> neighboors() const
    {
        std::vector<EcnPuzzle> res;
        for(const Puzzle &n : p.neighboors())
            res.push_back(EcnPuzzle(n));
        return res;
    }
    void print(const EcnPuzzle &next) const
    {
        std::cout << p.str() << " -> " << next.p.str() << "\n";
    }
};

void ecnDemo(const Puzzle &start, const Puzzle &goal)
{
    ecn::Astar(EcnPuzzle(start), EcnPuzzle(goal));
}
#endif

int main()
{
    const Puzzle goal(std::array<int, 9>{{1, 2, 3, 4, 5, 6, 7, 8, 0}});

    // Build a start by sliding the blank around from the goal (always solvable).
    Puzzle start = goal;
    const int scramble[] = {1, 3, 3, 0, 2, 1, 3, 0, 0, 2, 2, 1, 1, 3, 3, 0, 2, 1, 3, 0, 2, 1};
    for(int k : scramble)
        start.slide(k);
    std::cout << "start " << start.str() << "  goal " << goal.str() << "\n";
    std::cout << "solvable: " << (solvable(start, goal) ? "yes" : "no") << "\n";

    astar_snip::Stats st;
    const auto t0 = std::chrono::steady_clock::now();
    const std::vector<Puzzle> path = astarKeyed(start, goal,
        [](const Puzzle &p) { return p.str(); }, &st);   // ADAPT: key function
    const auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                        std::chrono::steady_clock::now() - t0).count();
    std::cout << "solution in " << moves(path) << " moves, "
              << st.expanded << " expanded, " << st.generated << " generated, "
              << ms << " ms\n";
    for(size_t i = 0; i < path.size(); ++i)
        std::cout << "  " << i << ": " << path[i].str() << "\n";

    // The same with the linear-lookup version (only needs ==), fine for small searches.
    const std::vector<Puzzle> path2 = astar(start, goal);
    std::cout << "linear version gives " << moves(path2) << " moves (must be equal)\n";

    // An unsolvable board: swap two tiles of the goal.
    const Puzzle bad(std::array<int, 9>{{2, 1, 3, 4, 5, 6, 7, 8, 0}});
    std::cout << bad.str() << " solvable: " << (solvable(bad, goal) ? "yes" : "no") << "\n";

#ifdef USE_ECN_ASTAR
    ecnDemo(start, goal);
#endif
    return 0;
}
