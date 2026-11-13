# STL quick reference (C++17)

## vector  `#include <vector>`

```cpp
std::vector<int> v;                 // empty
std::vector<int> v(5, 0);           // 5 zeros
std::vector<int> v{1,2,3};
std::vector<std::vector<int>> g(R, std::vector<int>(C, 0));   // R x C grid

v.push_back(4);        // copy/move in
v.emplace_back(4);     // construct in place (v.emplace_back(x, y) for a struct ctor)
v.pop_back();
v.back();  v.front();  // last / first element (UB if empty)
v[i];  v.at(i);        // at() throws out_of_range, [] does not check
v.size();  v.empty();  v.clear();
v.resize(10);          // changes size (new elements value-initialized)
v.reserve(100);        // capacity only, size unchanged (v[i] still invalid!)
v.insert(v.begin() + 2, 99);        // insert before index 2
v.insert(v.end(), w.begin(), w.end());   // append another vector
v.erase(v.begin() + 2);             // erase one
v.erase(v.begin() + 1, v.begin() + 3);   // erase range [1,3)
v.begin(); v.end();  v.rbegin(); v.rend();   // end() is ONE PAST the last element
```
**Erase by value (erase-remove idiom)** - vector has no `.remove()`:
```cpp
v.erase(std::remove(v.begin(), v.end(), 5), v.end());                 // all 5s
v.erase(std::remove_if(v.begin(), v.end(), [](int x){ return x < 0; }), v.end());
// erase first occurrence safely:
auto it = std::find(v.begin(), v.end(), 5);
if (it != v.end()) v.erase(it);     // NEVER erase(v.end())
```
Erase inside a loop:
```cpp
for (auto it = v.begin(); it != v.end(); ) {
    if (*it < 0) it = v.erase(it);  // erase returns next valid iterator
    else ++it;
}
```
Fast unordered delete: `std::swap(v[i], v.back()); v.pop_back();`

## array  `#include <array>`
```cpp
std::array<int, 5> a{};      // fixed size, on stack, zero-initialized with {}
a.size(); a[i]; a.fill(0); a.begin(); a.end();
std::array<Cell, 81> cells;  // size is part of the type; passes by value unless &
```

## deque / list
```cpp
#include <deque>
std::deque<int> d;  d.push_front(1);  d.push_back(2);  d.pop_front();  d.front(); d.back(); d[i];
#include <list>
std::list<int> l;   l.push_back(1);  l.push_front(0);  l.remove(5);   // list HAS remove(value)
l.erase(it);        l.sort();  l.reverse();   // no l[i]
```

## map / unordered_map  `#include <map>` / `<unordered_map>`
```cpp
std::map<std::string,int> m;             // sorted by key, O(log n), needs operator< on key
std::unordered_map<std::string,int> um;  // hash table, O(1) avg, no order, key needs hash+==

m["a"] = 1;                 // operator[] INSERTS default value if key missing!
m["zzz"];                   // creates "zzz" -> 0  (use find/count to only look)
m.insert({"b", 2});         // does nothing if key exists, returns pair<iterator,bool>
m.emplace("c", 3);
m.at("a");                  // throws if missing, does not insert
m.count("a");               // 0 or 1 (membership test)
auto it = m.find("a");      // m.end() if missing
if (it != m.end()) { it->first; it->second; }
m.erase("a");               // by key; m.erase(it) by iterator
m.size(); m.empty(); m.clear();
for (const auto& [k, v] : m) std::cout << k << v;      // sorted order for map
for (auto& kv : m) kv.second++;                        // kv is pair<const K,V>
```
Frequency count: `for (char c : s) ++freq[c];`
Key = struct: define `operator<` (map) or hash (unordered_map). A `std::pair<int,int>` key works with `map` directly, not with `unordered_map`.

## set / unordered_set
```cpp
std::set<int> s{3,1,2};      // sorted, unique, O(log n)
s.insert(4);  s.erase(4);  s.count(4);  s.find(4) != s.end();
*s.begin();  *s.rbegin();    // min / max
s.lower_bound(2);            // first >= 2
std::unordered_set<int> us;  us.insert(1);  us.count(1);   // O(1) avg
std::set<std::pair<int,int>> visited;  visited.insert({x,y});
```
Visited-set pattern in search: `if (!visited.insert(state).second) continue;` (insert returns false if already present).

## pair / tuple
```cpp
#include <utility>
std::pair<int,std::string> p{1, "a"};  p.first; p.second;  auto p2 = std::make_pair(1, 2);
p < q            // lexicographic compare
#include <tuple>
std::tuple<int,double,char> t{1, 2.0, 'c'};
std::get<0>(t);  auto [a,b,c] = t;  std::tie(a,b,c) = t;
```

## priority_queue  `#include <queue>`
```cpp
std::priority_queue<int> maxpq;                                   // MAX-heap by default (top = largest)
std::priority_queue<int, std::vector<int>, std::greater<int>> minpq;   // MIN-heap
pq.push(x);  pq.top();  pq.pop();  pq.empty();  pq.size();        // pop() returns void! read top() first
```
Pairs: `priority_queue<pair<double,int>, vector<...>, greater<...>>` pops smallest cost first.

Custom comparator struct (the "less" semantic is inverted: the element for which cmp is "less" sinks, so to get a min-heap on cost, use `>`):
```cpp
struct Cmp {
    bool operator()(const Node& a, const Node& b) const { return a.f() > b.f(); }  // smallest f on top
};
std::priority_queue<Node, std::vector<Node>, Cmp> open;
```
Lambda comparator:
```cpp
auto cmp = [](const Node& a, const Node& b) { return a.f() > b.f(); };
std::priority_queue<Node, std::vector<Node>, decltype(cmp)> open(cmp);
```
No decrease-key: push a duplicate with the better cost, skip stale entries when popped (`if (closed.count(n)) continue;`).

## queue / stack
```cpp
std::queue<int> q;  q.push(1); q.front(); q.back(); q.pop(); q.empty(); q.size();   // BFS (FIFO)
std::stack<int> st; st.push(1); st.top();   st.pop(); st.empty();                   // DFS (LIFO)
```
pop() returns nothing: `int x = q.front(); q.pop();`

## string  `#include <string>`
```cpp
std::string s = "hello world";
s.size(); s.length(); s.empty(); s[0]; s.back(); s.front();
s.substr(pos, len);          // s.substr(6) = "world", s.substr(0,5) = "hello"
s.find("lo");                // index or std::string::npos if missing
if (s.find("x") == std::string::npos) { /* not found */ }
s.find('o', 5);              // search from pos 5;  s.rfind('o')
s += "!";  s.push_back('c');  s.append("x");  s.insert(0, "> ");  s.erase(0, 2);  s.replace(0, 5, "HELLO");
s == t;  s < t;  s.compare(t);
std::to_string(42);  std::to_string(3.14);
std::stoi("42");  std::stod("3.5");  std::stol("9");     // throw invalid_argument if bad
std::string(3, 'a');   // "aaa"
std::reverse(s.begin(), s.end());
std::toupper(c); std::isdigit(c); std::isalpha(c);       // <cctype>, char args
const char* cs = s.c_str();
```
Split (stringstream):
```cpp
#include <sstream>
std::vector<std::string> split(const std::string& line, char sep) {
    std::vector<std::string> out; std::string tok;
    std::stringstream ss(line);
    while (std::getline(ss, tok, sep)) out.push_back(tok);
    return out;
}
std::istringstream in("1 2 3");  int a, b, c;  in >> a >> b >> c;   // whitespace split
std::ostringstream os;  os << "x=" << 5;  os.str();                  // build a string
```
File read: `std::ifstream f("in.txt"); std::string line; while (std::getline(f, line)) {...}` (`<fstream>`).

## <algorithm>
```cpp
#include <algorithm>
std::sort(v.begin(), v.end());                                  // ascending
std::sort(v.begin(), v.end(), std::greater<int>());             // descending
std::sort(v.begin(), v.end(), [](const P& a, const P& b) { return a.cost < b.cost; });
std::stable_sort(...);                                          // keeps order of equals
```
Comparator must be a strict weak ordering (`<`, never `<=`) or sort can crash.
```cpp
auto it = std::find(v.begin(), v.end(), 5);                     // end() if absent
auto it = std::find_if(v.begin(), v.end(), [](int x){ return x > 3; });
std::count(v.begin(), v.end(), 5);
std::count_if(v.begin(), v.end(), [](int x){ return x % 2 == 0; });
std::all_of(v.begin(), v.end(), pred);  std::any_of(...);  std::none_of(...);   // return bool
std::binary_search(v.begin(), v.end(), x);                      // sorted input only
std::lower_bound(v.begin(), v.end(), x);                        // first >= x, sorted input
```
### min_element / max_element (semantics!)
```cpp
auto it = std::min_element(v.begin(), v.end());                 // uses <
auto it = std::min_element(v.begin(), v.end(),
        [](const Cell& a, const Cell& b) { return a.candidates().size() < b.candidates().size(); });
```
- Comparator `comp(a, b)` returns **true if a is "better"/smaller than b**; min_element returns the best.
- Returns an ITERATOR: use `*it` (value) or `it->member`, `std::distance(v.begin(), it)` for the index. Empty range returns `end()`.
- Rule out invalid items first so they never win:
```cpp
[](const Cell& a, const Cell& b) {
    if (a.digit()) return false;     // a already filled: never better
    if (b.digit()) return true;      // b filled: a is better
    return a.candidates().size() < b.candidates().size();
}
```
- `max_element` with comparator: same `comp`, returns the element for which no other is "greater".
- For a container of non-copyable objects, take `const auto&` params.

### numeric / misc
```cpp
#include <numeric>
std::accumulate(v.begin(), v.end(), 0);        // sum; init type matters: use 0.0 for doubles!
std::accumulate(v.begin(), v.end(), 0.0, [](double s, const P& p){ return s + p.cost; });
std::iota(v.begin(), v.end(), 0);              // 0,1,2,... (fill a permutation)
std::reverse(v.begin(), v.end());
std::unique(v.begin(), v.end());               // removes CONSECUTIVE dups: sort first; then erase:
v.erase(std::unique(v.begin(), v.end()), v.end());
std::swap(a, b);  std::iter_swap(it1, it2);
std::fill(v.begin(), v.end(), 0);
std::copy(a.begin(), a.end(), b.begin());
std::next_permutation(v.begin(), v.end());     // sorted start => all permutations (do-while)
std::min(a, b); std::max(a, b); std::min({a,b,c});   std::clamp(x, lo, hi);
std::distance(v.begin(), it);                  // index of iterator
std::advance(it, 3);
std::shuffle(v.begin(), v.end(), rng);         // needs <random> engine (std::random_shuffle removed in C++17)
std::rotate(v.begin(), v.begin()+1, v.end());
```

## Iterator invalidation
| Container | Operation | Invalidates |
|-----------|-----------|-------------|
| vector | push_back / insert / emplace | ALL iterators/pointers/refs if it reallocates (size > capacity), else those after the point |
| vector | erase(it) | `it` and everything after (use the returned iterator) |
| vector | resize/reserve beyond capacity | all |
| deque | insert/erase in the middle | all; push_front/back invalidates iterators but not references |
| list, map, set | insert | nothing |
| list, map, set | erase(it) | only `it` (use `it = c.erase(it)`) |
| unordered_* | insert causing rehash | iterators (references to elements stay valid) |

Rules: do not push_back to a vector while range-for iterating it; do not keep `&v[0]` / `Cell*` across a push_back; never `erase(v.end())`; never dereference `end()`.

## <random>
```cpp
#include <random>
std::random_device rd;                           // non-deterministic seed
std::mt19937 rng(rd());                          // seeded engine; use std::mt19937 rng(42); for reproducible runs
std::uniform_int_distribution<int> dist(0, 9);   // INCLUSIVE [0, 9]
int r = dist(rng);
std::uniform_real_distribution<double> ur(0.0, 1.0);   // [0, 1)
double p = ur(rng);
std::normal_distribution<double> nd(0.0, 1.0);
std::bernoulli_distribution coin(0.3);   coin(rng);    // true with prob 0.3
// pick random index of a vector:
std::uniform_int_distribution<size_t> pick(0, v.size() - 1);
v[pick(rng)];
std::shuffle(v.begin(), v.end(), rng);
```
Make `rng` a global/static or pass by reference; do not re-create it in a hot loop.

## <chrono> timing
```cpp
#include <chrono>
auto t0 = std::chrono::steady_clock::now();
/* ... work ... */
auto t1 = std::chrono::steady_clock::now();
auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();
double sec = std::chrono::duration<double>(t1 - t0).count();
std::cout << ms << " ms\n";
```
Time-limited loop: `while (std::chrono::steady_clock::now() - t0 < std::chrono::seconds(5)) {...}`

## <cmath>
```cpp
#include <cmath>
std::sqrt(x);  std::pow(x, 2);  std::hypot(dx, dy);       // hypot = sqrt(dx*dx+dy*dy), the Euclidean distance
std::abs(x);   // use std::abs with <cmath>/<cstdlib>: plain abs(double) may call the int version
std::fabs(x);  std::floor(x);  std::ceil(x);  std::round(x);
std::exp(x); std::log(x); std::sin(x); std::cos(x); std::atan2(y, x);
M_PI                                             // may need -D_USE_MATH_DEFINES on non-Linux
std::numeric_limits<double>::infinity();  std::numeric_limits<int>::max();   // <limits>
std::isnan(x);
```
Manhattan: `std::abs(x1-x2) + std::abs(y1-y2)`; Euclidean: `std::hypot(x1-x2, y1-y2)`. With unsigned coords cast to int first.
