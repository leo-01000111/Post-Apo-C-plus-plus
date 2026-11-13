// containers_tricks.cpp - STL containers / algorithms you need under exam pressure.
// Build: g++ -std=c++17 -Wall -Wextra -O2 containers_tricks.cpp -o containers_tricks
//
// Contents:
//   1. priority_queue as MIN-heap: std::greater, comparator struct, lambda
//   2. map / unordered_map with a custom key (pair<int,int> and a struct), custom hash
//   3. set of structs with operator<
//   4. erase-remove idiom (and std::erase_if equivalent without C++20)
//   5. sort by several keys (std::tie and explicit lambda)
//   6. std::min_element / max_element with comparator (sudoku "most constrained cell")
//   7. misc one-liners (find_if, count_if, accumulate, lower_bound, unique)
#include <algorithm>
#include <cstddef>
#include <functional>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <set>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

struct Task
{
    int cost;
    std::string name;
};

// 1. priority_queue is a MAX-heap: top() = largest according to "less".
//    For a MIN-heap the comparator must say "a is worse than b" when a > b.
// 1a. integers: std::greater
using MinHeapInt = std::priority_queue<int, std::vector<int>, std::greater<int>>;

// 1b. comparator struct (reusable, e.g. for A* open set). ADAPT: the member compared.
struct TaskWorse
{
    bool operator()(const Task &a, const Task &b) const { return a.cost > b.cost; }
};
using TaskQueue = std::priority_queue<Task, std::vector<Task>, TaskWorse>;

// 1c. pair<f, id> works out of the box with std::greater (compares first, then second)
using FQueue = std::priority_queue<std::pair<double, int>,
                                   std::vector<std::pair<double, int>>,
                                   std::greater<std::pair<double, int>>>;

void demoPriorityQueue()
{
    MinHeapInt h;
    for(int v : {5, 1, 8, 3})
        h.push(v);
    std::cout << "min-heap pops:";
    while(!h.empty())
    {
        std::cout << ' ' << h.top();
        h.pop();
    }
    std::cout << "\n";

    TaskQueue tq;
    tq.push({7, "seven"});
    tq.push({2, "two"});
    tq.push({4, "four"});
    std::cout << "cheapest task: " << tq.top().name << "\n";

    // lambda comparator: needs decltype and the lambda passed to the constructor
    auto cmp = [](const Task &a, const Task &b) { return a.name > b.name; };
    std::priority_queue<Task, std::vector<Task>, decltype(cmp)> byName(cmp);
    byName.push({1, "pear"});
    byName.push({2, "apple"});
    byName.push({3, "zebra"});
    std::cout << "first alphabetically: " << byName.top().name << "\n";

    FQueue fq;
    fq.push(std::make_pair(3.5, 10));
    fq.push(std::make_pair(1.5, 20));
    std::cout << "smallest f: " << fq.top().first << " id " << fq.top().second << "\n";
}

// 2. Custom keys
// 2a. std::map works with pair<int,int> directly (pair has operator<). O(log n).
// 2b. unordered_map needs a hash. Hash for pair<int,int>:
struct PairHash
{
    size_t operator()(const std::pair<int, int> &p) const
    {
        const unsigned long long a = static_cast<unsigned int>(p.first);
        const unsigned long long b = static_cast<unsigned int>(p.second);
        return std::hash<unsigned long long>()((a << 32) | b);
    }
};

// 2c. a struct as key: needs operator== (unordered) or operator< (ordered) + hash.
struct Pos
{
    int x, y;
    bool operator==(const Pos &o) const { return x == o.x && y == o.y; }
    bool operator<(const Pos &o) const { return std::tie(x, y) < std::tie(o.x, o.y); }
};
struct PosHash
{
    size_t operator()(const Pos &p) const
    {
        // classic hash combine
        size_t h = std::hash<int>()(p.x);
        h ^= std::hash<int>()(p.y) + 0x9e3779b9u + (h << 6) + (h >> 2);
        return h;
    }
};

void demoMaps()
{
    std::map<std::pair<int, int>, int> ordered;
    ordered[std::make_pair(1, 2)] = 10;
    ordered[std::make_pair(0, 5)] = 20;
    std::cout << "ordered map first key: (" << ordered.begin()->first.first << ","
              << ordered.begin()->first.second << ")\n";

    std::unordered_map<std::pair<int, int>, int, PairHash> visited;
    visited[std::make_pair(3, 4)] = 1;
    visited[std::make_pair(-3, 4)] = 2;
    const bool has = visited.find(std::make_pair(3, 4)) != visited.end();
    std::cout << "visited has (3,4): " << (has ? "yes" : "no")
              << ", count (9,9): " << visited.count(std::make_pair(9, 9)) << "\n";

    std::unordered_map<Pos, std::string, PosHash> names;
    names[Pos{1, 1}] = "one-one";
    std::cout << "names[(1,1)] = " << names[Pos{1, 1}] << "\n";

    std::unordered_set<std::string> seen;           // string keys need nothing special
    std::cout << "insert 'abc' new? " << seen.insert("abc").second
              << ", again new? " << seen.insert("abc").second << "\n";
}

// 3. set of structs (sorted, unique). Elements are compared with operator<
//    (two items are "equal" if neither is smaller). ADAPT: the fields in tie().
struct Person
{
    std::string name;
    int age;
    bool operator<(const Person &o) const { return std::tie(age, name) < std::tie(o.age, o.name); }
};

void demoSet()
{
    std::set<Person> people;
    people.insert({"Zed", 30});
    people.insert({"Amy", 25});
    people.insert({"Bob", 30});
    people.insert({"Amy", 25});    // duplicate ignored
    std::cout << "set size " << people.size() << ", order:";
    for(const Person &p : people)
        std::cout << ' ' << p.name << '(' << p.age << ')';
    std::cout << "\n";
    // lower_bound: first element not less than the probe
    auto it = people.lower_bound(Person{"", 30});
    std::cout << "first aged >= 30: " << it->name << "\n";
}

// 4. erase-remove idiom. remove_if only MOVES the kept items to the front and
//    returns the new end; erase then shrinks the vector.
void demoEraseRemove()
{
    std::vector<int> v{1, 2, 3, 4, 5, 6, 7, 8};
    v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; }), v.end());
    std::cout << "odd only:";
    for(int x : v)
        std::cout << ' ' << x;
    std::cout << "\n";

    std::vector<int> w{3, 1, 3, 2, 3};
    w.erase(std::remove(w.begin(), w.end(), 3), w.end());
    std::cout << "without 3s: " << w.size() << " items\n";

    std::vector<int> d{1, 1, 2, 2, 2, 3, 1};
    std::sort(d.begin(), d.end());
    d.erase(std::unique(d.begin(), d.end()), d.end());          // dedupe (needs sorted)
    std::cout << "unique sorted: " << d.size() << " items\n";

    // Removing while iterating by index: remember to NOT increment after erase.
    std::vector<int> e{1, 2, 2, 3};
    for(size_t i = 0; i < e.size();)
    {
        if(e[i] == 2)
            e.erase(e.begin() + static_cast<std::ptrdiff_t>(i));
        else
            ++i;
    }
    std::cout << "manual erase left " << e.size() << " items\n";
}

// 5. Sorting by several keys
void demoSort()
{
    std::vector<Task> t{{3, "c"}, {1, "z"}, {3, "a"}, {1, "b"}};
    // cost ascending, then name ascending
    std::sort(t.begin(), t.end(), [](const Task &a, const Task &b)
              { return std::tie(a.cost, a.name) < std::tie(b.cost, b.name); });
    std::cout << "cost asc, name asc:";
    for(const Task &x : t)
        std::cout << ' ' << x.cost << x.name;
    std::cout << "\n";

    // cost DESCENDING, then name ascending (mix directions with an explicit lambda)
    std::sort(t.begin(), t.end(), [](const Task &a, const Task &b)
              {
                  if(a.cost != b.cost)
                      return a.cost > b.cost;
                  return a.name < b.name;
              });
    std::cout << "cost desc, name asc:";
    for(const Task &x : t)
        std::cout << ' ' << x.cost << x.name;
    std::cout << "\n";

    // stable_sort keeps the previous order among equal elements
    std::stable_sort(t.begin(), t.end(), [](const Task &a, const Task &b) { return a.cost < b.cost; });
}

// 6. min_element with a comparator. Returns an ITERATOR (end() if empty!).
//    comparator(a, b) == "a is smaller than b". Sudoku: pick cell with fewest candidates.
struct Cell
{
    int id;
    std::vector<int> candidates;
};

void demoMinElement()
{
    std::vector<Cell> cells{{0, {1, 2, 3}}, {1, {4}}, {2, {5, 6}}};
    auto it = std::min_element(cells.begin(), cells.end(),
        [](const Cell &a, const Cell &b) { return a.candidates.size() < b.candidates.size(); });
    if(it != cells.end())
        std::cout << "most constrained cell: " << it->id << " ("
                  << it->candidates.size() << " candidate)\n";

    // among pointers (typical when the grid owns the cells)
    std::vector<Cell *> ptrs;
    for(Cell &c : cells)
        ptrs.push_back(&c);
    auto itp = std::max_element(ptrs.begin(), ptrs.end(),
        [](const Cell *a, const Cell *b) { return a->candidates.size() < b->candidates.size(); });
    std::cout << "least constrained cell: " << (*itp)->id << "\n";

    // skip already-decided cells: filter FIRST (copy the undecided ones) then min_element
    std::vector<Cell *> todo;
    for(Cell *c : ptrs)
        if(c->candidates.size() > 1)
            todo.push_back(c);
    std::cout << "undecided cells: " << todo.size() << "\n";
}

// 7. Misc one-liners
void demoMisc()
{
    std::vector<int> v{4, 8, 15, 16, 23, 42};
    auto f = std::find_if(v.begin(), v.end(), [](int x) { return x > 15; });
    std::cout << "first > 15: " << *f << " at index " << (f - v.begin()) << "\n";
    std::cout << "count even: " << std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; })
              << "\n";
    std::cout << "sum: " << std::accumulate(v.begin(), v.end(), 0) << "\n";
    auto lb = std::lower_bound(v.begin(), v.end(), 16);     // sorted input only
    std::cout << "lower_bound(16) index: " << (lb - v.begin()) << "\n";
    std::cout << "any/all/none: " << std::any_of(v.begin(), v.end(), [](int x) { return x == 8; })
              << std::all_of(v.begin(), v.end(), [](int x) { return x > 0; })
              << std::none_of(v.begin(), v.end(), [](int x) { return x > 100; }) << "\n";
    std::reverse(v.begin(), v.end());
    std::rotate(v.begin(), v.begin() + 1, v.end());         // left-rotate by 1
    std::cout << "after reverse+rotate front = " << v.front() << "\n";
    // iota + shuffle indices is in random_timing.cpp
}

int main()
{
    demoPriorityQueue();
    demoMaps();
    demoSet();
    demoEraseRemove();
    demoSort();
    demoMinElement();
    demoMisc();
    return 0;
}
