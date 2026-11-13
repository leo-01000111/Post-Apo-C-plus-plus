# C++17 standard-library syntax reference (offline exam kit).
# Every `ex` is compile-checked by test_functions.py (python site_src/test_functions.py).
# Plain ASCII only.

FUNCTIONS = []


def E(name, scope, header, sig, ex, cx="", note=""):
    FUNCTIONS.append({
        "name": name,
        "scope": scope,
        "header": header,
        "sig": sig.strip("\n"),
        "ex": ex.strip("\n"),
        "cx": cx,
        "note": note,
    })


# ---------------------------------------------------------------- vector
S = "vector"
H = "<vector>"
E("push_back", S, H,
  "void v.push_back(const T& x);\nvoid v.push_back(T&& x);",
  r'''std::vector<int> v{1,2};
v.push_back(3);   // v = {1,2,3}''',
  "amortised O(1)", "Reallocation invalidates all iterators, pointers and references into v.")
E("emplace_back", S, H,
  "T& v.emplace_back(args...);",
  r'''std::vector<std::pair<int,int>> v;
v.emplace_back(1, 2);   // builds the pair in place, no temporary''',
  "amortised O(1)", "Pass the constructor arguments, not an already-built object.")
E("pop_back", S, H,
  "void v.pop_back();",
  r'''std::vector<int> v{1,2,3};
v.pop_back();   // v = {1,2}''',
  "O(1)", "UB if empty. Returns nothing: read v.back() first.")
E("back", S, H,
  "T& v.back();",
  r'''std::vector<int> v{1,2,3};
int x = v.back();   // 3''',
  "O(1)", "UB if empty. Returns a reference, not an iterator.")
E("front", S, H,
  "T& v.front();",
  r'''std::vector<int> v{1,2,3};
int x = v.front();   // 1''',
  "O(1)", "UB if empty.")
E("at", S, H,
  "T& v.at(size_t i);",
  r'''std::vector<int> v{1,2,3};
int x = v.at(1);   // 2; v.at(9) throws std::out_of_range''',
  "O(1)", "Bounds-checked, throws std::out_of_range.")
E("operator[]", S, H,
  "T& v[size_t i];",
  r'''std::vector<int> v{1,2,3};
v[0] = 10;   // v = {10,2,3}''',
  "O(1)", "No bounds check: out-of-range is UB. Never grows the vector.")
E("size", S, H,
  "size_t v.size();",
  r'''std::vector<int> v{1,2,3};
size_t n = v.size();   // 3''',
  "O(1)", "Unsigned: v.size() - 1 wraps to a huge value when empty. Cast to int if you subtract.")
E("empty", S, H,
  "bool v.empty();",
  r'''std::vector<int> v;
bool e = v.empty();   // true''',
  "O(1)", "Prefer it over size() == 0.")
E("clear", S, H,
  "void v.clear();",
  r'''std::vector<int> v{1,2,3};
v.clear();   // size 0, capacity unchanged''',
  "O(n)", "Does not release memory.")
E("resize", S, H,
  "void v.resize(size_t n);\nvoid v.resize(size_t n, const T& val);",
  r'''std::vector<int> v{1,2};
v.resize(4, 9);   // v = {1,2,9,9}''',
  "O(n)", "Shrinks or grows; new elements are value-initialised (0) unless val is given.")
E("reserve", S, H,
  "void v.reserve(size_t n);",
  r'''std::vector<int> v;
v.reserve(100);   // size still 0, no reallocation until 100 elements''',
  "O(n)", "Changes capacity only, not size: v[5] is still invalid afterwards.")
E("insert", S, H,
  "It v.insert(It pos, const T& x);\nIt v.insert(It pos, size_t n, const T& x);\nIt v.insert(It pos, It first, It last);",
  r'''std::vector<int> v{1,3};
v.insert(v.begin() + 1, 2);   // v = {1,2,3}''',
  "O(n)", "Inserts BEFORE pos. Returns iterator to the first inserted element.")
E("erase", S, H,
  "It v.erase(It pos);\nIt v.erase(It first, It last);",
  r'''std::vector<int> v{1,2,3};
v.erase(v.begin() + 1);   // v = {1,3}''',
  "O(n)", "Returns the iterator after the erased element; use it when erasing in a loop. [first,last) is half-open.")
E("begin / end", S, H,
  "It v.begin();\nIt v.end();",
  r'''std::vector<int> v{1,2,3};
for (auto it = v.begin(); it != v.end(); ++it) *it += 1;   // {2,3,4}''',
  "O(1)", "end() is one PAST the last element: never dereference it.")
E("rbegin / rend", S, H,
  "RevIt v.rbegin();\nRevIt v.rend();",
  r'''std::vector<int> v{1,2,3};
for (auto it = v.rbegin(); it != v.rend(); ++it) std::cout << *it;   // 321''',
  "O(1)", "Reverse iterators still use ++ to move toward the front.")
E("assign", S, H,
  "void v.assign(size_t n, const T& val);\nvoid v.assign(It first, It last);",
  r'''std::vector<int> v;
v.assign(3, 7);   // v = {7,7,7}''',
  "O(n)", "Replaces the whole content.")
E("data", S, H,
  "T* v.data();",
  r'''std::vector<int> v{1,2,3};
int* p = v.data();   // raw array, p[1] == 2''',
  "O(1)", "Pointer is invalidated by reallocation. Use for C APIs.")

# ---------------------------------------------------------------- array
S = "array"
H = "<array>"
E("size", S, H,
  "constexpr size_t a.size();",
  r'''std::array<int,3> a{1,2,3};
size_t n = a.size();   // 3''',
  "O(1)", "Size is part of the type: std::array<int,3> is fixed, cannot grow.")
E("fill", S, H,
  "void a.fill(const T& val);",
  r'''std::array<int,3> a{};
a.fill(5);   // a = {5,5,5}''',
  "O(n)", "")
E("at", S, H,
  "T& a.at(size_t i);",
  r'''std::array<int,3> a{1,2,3};
int x = a.at(2);   // 3; a.at(3) throws std::out_of_range''',
  "O(1)", "Bounds-checked; a[i] is not.")

# ---------------------------------------------------------------- deque
S = "deque"
H = "<deque>"
E("push_front", S, H,
  "void d.push_front(const T& x);",
  r'''std::deque<int> d{2,3};
d.push_front(1);   // d = {1,2,3}''',
  "O(1)", "vector has no push_front.")
E("pop_front", S, H,
  "void d.pop_front();",
  r'''std::deque<int> d{1,2,3};
d.pop_front();   // d = {2,3}''',
  "O(1)", "UB if empty. Returns nothing: read d.front() first.")
E("emplace_front", S, H,
  "T& d.emplace_front(args...);",
  r'''std::deque<std::pair<int,int>> d;
d.emplace_front(1, 2);   // builds the pair in place at the front''',
  "O(1)", "")

# ---------------------------------------------------------------- list
S = "list"
H = "<list>"
E("push_front", S, H,
  "void l.push_front(const T& x);",
  r'''std::list<int> l{2,3};
l.push_front(1);   // l = {1,2,3}''',
  "O(1)", "No operator[]: lists are not random access.")
E("splice", S, H,
  "void l.splice(It pos, list& other);\nvoid l.splice(It pos, list& other, It it);",
  r'''std::list<int> a{1,2}, b{3,4};
a.splice(a.end(), b);   // a = {1,2,3,4}, b = {}''',
  "O(1)", "Moves nodes, no copy; other loses the elements.")
E("remove", S, H,
  "void l.remove(const T& val);\nvoid l.remove_if(pred);",
  r'''std::list<int> l{1,2,2,3};
l.remove(2);   // l = {1,3}''',
  "O(n)", "Member function that really erases (unlike std::remove). Also l.sort(), l.unique(), l.reverse() are members.")

# ---------------------------------------------------------------- map / unordered_map
S = "map / unordered_map"
H = "<map> / <unordered_map>"
E("operator[]", S, H,
  "V& m[key];",
  r'''std::map<std::string,int> m;
m["a"]++;   // inserts "a" with 0, then 1''',
  "O(log n) map / O(1) avg unordered", "INSERTS a default value if the key is missing (so reading m[k] can grow the map). Not usable on a const map.")
E("at", S, H,
  "V& m.at(key);",
  r'''std::map<std::string,int> m{{"a",1}};
int x = m.at("a");   // 1; m.at("z") throws std::out_of_range''',
  "O(log n) map / O(1) avg unordered", "Never inserts; throws if the key is missing.")
E("find", S, H,
  "It m.find(key);",
  r'''std::unordered_map<std::string,int> m{{"a",1}};
auto it = m.find("a");
if (it != m.end()) int v = it->second;   // it->first is the key''',
  "O(log n) map / O(1) avg unordered", "Returns m.end() if not found.")
E("count", S, H,
  "size_t m.count(key);",
  r'''std::unordered_map<int,int> m{{1,10}};
bool has = m.count(1) > 0;   // true''',
  "O(log n) map / O(1) avg unordered", "Returns 0 or 1 (keys are unique). Does not insert.")
E("insert", S, H,
  "pair<It,bool> m.insert({key, val});\npair<It,bool> m.insert(make_pair(key, val));",
  r'''std::map<std::string,int> m;
auto r = m.insert({"a", 1});   // r.second == true if inserted''',
  "O(log n) map / O(1) avg unordered", "Does NOT overwrite an existing key (r.second is false). Use insert_or_assign or m[k] = v to overwrite.")
E("emplace", S, H,
  "pair<It,bool> m.emplace(key, val);",
  r'''std::map<std::string,int> m;
m.emplace("a", 1);   // constructs the pair in place''',
  "O(log n) map / O(1) avg unordered", "Does not overwrite an existing key.")
E("try_emplace", S, H,
  "pair<It,bool> m.try_emplace(key, args...);",
  r'''std::map<std::string,std::string> m;
m.try_emplace("a", "hello");   // C++17''',
  "O(log n) map / O(1) avg unordered", "If the key exists nothing happens and args are not consumed (unlike emplace).")
E("insert_or_assign", S, H,
  "pair<It,bool> m.insert_or_assign(key, val);",
  r'''std::map<std::string,int> m{{"a",1}};
m.insert_or_assign("a", 5);   // m["a"] == 5, returns {it, false}''',
  "O(log n) map / O(1) avg unordered", "C++17. Overwrites if present, inserts otherwise.")
E("erase", S, H,
  "size_t m.erase(key);\nIt m.erase(It pos);",
  r'''std::map<std::string,int> m{{"a",1},{"b",2}};
m.erase("a");   // m = {{"b",2}}''',
  "O(log n) map / O(1) avg unordered", "Erasing by key returns the number removed (0 if absent). Erasing by iterator invalidates only that iterator.")
E("structured-binding iteration", S, H,
  "for (auto& [key, val] : m) { ... }\nfor (const auto& [key, val] : m) { ... }",
  r'''std::map<std::string,int> m{{"a",1},{"b",2}};
for (const auto& [k, v] : m) std::cout << k << "=" << v << "\n";''',
  "O(n)", "C++17. std::map iterates in sorted key order; unordered_map in arbitrary order. Use auto& to modify val.")
E("lower_bound", S, H,
  "It m.lower_bound(key);\nIt m.upper_bound(key);",
  r'''std::map<int,char> m{{1,'a'},{5,'b'}};
auto it = m.lower_bound(3);   // points to {5,'b'}''',
  "O(log n)", "std::map only (not unordered_map). First key >= given; upper_bound is first key > given. end() if none.")

# ---------------------------------------------------------------- set / unordered_set
S = "set / unordered_set"
H = "<set> / <unordered_set>"
E("insert", S, H,
  "pair<It,bool> s.insert(const T& x);",
  r'''std::set<int> s;
auto r = s.insert(5);   // r.second == true if newly added''',
  "O(log n) set / O(1) avg unordered", "Duplicates are ignored (r.second is false). set keeps elements sorted.")
E("find", S, H,
  "It s.find(const T& x);",
  r'''std::set<int> s{1,2,3};
bool has = s.find(2) != s.end();   // true''',
  "O(log n) set / O(1) avg unordered", "Returns s.end() if not found. Do not use std::find on a set (O(n)).")
E("count", S, H,
  "size_t s.count(const T& x);",
  r'''std::unordered_set<int> s{1,2,3};
if (s.count(2)) { /* present */ }''',
  "O(log n) set / O(1) avg unordered", "Returns 0 or 1.")
E("erase", S, H,
  "size_t s.erase(const T& x);\nIt s.erase(It pos);",
  r'''std::set<int> s{1,2,3};
s.erase(2);   // s = {1,3}''',
  "O(log n) set / O(1) avg unordered", "By value returns number removed (0 or 1).")
E("lower_bound", S, H,
  "It s.lower_bound(const T& x);",
  r'''std::set<int> s{1,5,9};
auto it = s.lower_bound(4);   // points to 5''',
  "O(log n)", "std::set only. First element >= x, else end(). Prefer over std::lower_bound(s.begin(), ...) which is O(n) on a set.")
E("upper_bound", S, H,
  "It s.upper_bound(const T& x);",
  r'''std::set<int> s{1,5,9};
auto it = s.upper_bound(5);   // points to 9''',
  "O(log n)", "std::set only. First element > x, else end().")
E("begin", S, H,
  "It s.begin();\nRevIt s.rbegin();",
  r'''std::set<int> s{3,1,2};
int smallest = *s.begin();    // 1
int largest = *s.rbegin();    // 3''',
  "O(1)", "set iterates in ascending order, so *s.begin() is the min and *s.rbegin() the max. UB to dereference if empty.")

# ---------------------------------------------------------------- priority_queue
S = "priority_queue"
H = "<queue>"
E("push", S, H,
  "void pq.push(const T& x);",
  r'''std::priority_queue<int> pq;
pq.push(5); pq.push(9);   // top() is 9''',
  "O(log n)", "Default is a MAX-heap.")
E("emplace", S, H,
  "void pq.emplace(args...);",
  r'''std::priority_queue<std::pair<int,int>> pq;
pq.emplace(3, 1);   // builds the pair in place''',
  "O(log n)", "")
E("top", S, H,
  "const T& pq.top();",
  r'''std::priority_queue<int> pq;
pq.push(5); pq.push(9);
int x = pq.top();   // 9''',
  "O(1)", "UB if empty. Read-only reference to the largest element.")
E("pop", S, H,
  "void pq.pop();",
  r'''std::priority_queue<int> pq;
pq.push(5); pq.push(9);
pq.pop();   // removes 9''',
  "O(log n)", "Returns nothing: read top() first. UB if empty.")
E("empty", S, H,
  "bool pq.empty();",
  r'''std::priority_queue<int> pq;
while (!pq.empty()) pq.pop();''',
  "O(1)", "")
E("size", S, H,
  "size_t pq.size();",
  r'''std::priority_queue<int> pq;
pq.push(1);
size_t n = pq.size();   // 1''',
  "O(1)", "")
E("min-heap declaration", S, "<queue>, <functional>",
  "std::priority_queue<T, std::vector<T>, std::greater<T>> pq;",
  r'''std::priority_queue<int, std::vector<int>, std::greater<int>> pq;
pq.push(5); pq.push(2);
int x = pq.top();   // 2 (smallest)''',
  "", "For pairs the smallest .first comes out first (lexicographic).")
E("custom comparator declaration", S, "<queue>",
  "struct Cmp { bool operator()(const T& a, const T& b) const { return ...; } };\nstd::priority_queue<T, std::vector<T>, Cmp> pq;\nauto cmp = [](const T& a, const T& b){ return ...; };\nstd::priority_queue<T, std::vector<T>, decltype(cmp)> pq(cmp);",
  r'''auto cmp = [](const std::pair<int,int>& a, const std::pair<int,int>& b) { return a.second > b.second; };
std::priority_queue<std::pair<int,int>, std::vector<std::pair<int,int>>, decltype(cmp)> pq(cmp);
pq.push({1, 9}); pq.push({2, 3});   // top() is {2,3}: smallest .second''',
  "", "Comparator is inverted vs sort: cmp(a,b) true means a has LOWER priority (a comes out after b). With '>' you get a min-heap. The lambda form needs pq(cmp) in the constructor.")

# ---------------------------------------------------------------- queue / stack
S = "queue / stack"
E("push", S, "<queue>",
  "void q.push(const T& x);",
  r'''std::queue<int> q;
q.push(1); q.push(2);   // front 1, back 2''',
  "O(1)", "queue: FIFO. Adds at the back.")
E("front", S, "<queue>",
  "T& q.front();",
  r'''std::queue<int> q;
q.push(1); q.push(2);
int x = q.front();   // 1''',
  "O(1)", "UB if empty.")
E("back", S, "<queue>",
  "T& q.back();",
  r'''std::queue<int> q;
q.push(1); q.push(2);
int x = q.back();   // 2''',
  "O(1)", "UB if empty. Only queue has back(), priority_queue does not.")
E("pop", S, "<queue>",
  "void q.pop();",
  r'''std::queue<int> q;
q.push(1); q.push(2);
q.pop();   // removes 1''',
  "O(1)", "Removes the front, returns nothing: read q.front() first. UB if empty.")
E("push", S, "<stack>",
  "void st.push(const T& x);",
  r'''std::stack<int> st;
st.push(1); st.push(2);   // top is 2''',
  "O(1)", "stack: LIFO.")
E("top", S, "<stack>",
  "T& st.top();",
  r'''std::stack<int> st;
st.push(1); st.push(2);
int x = st.top();   // 2''',
  "O(1)", "UB if empty.")
E("pop", S, "<stack>",
  "void st.pop();",
  r'''std::stack<int> st;
st.push(1); st.push(2);
st.pop();   // removes 2''',
  "O(1)", "Returns nothing: read st.top() first. UB if empty.")

# ---------------------------------------------------------------- string
S = "string"
H = "<string>"
E("size / length", S, H,
  "size_t s.size();\nsize_t s.length();",
  r'''std::string s = "hello";
size_t n = s.size();   // 5''',
  "O(1)", "Identical functions. Unsigned: s.size() - 1 wraps when empty.")
E("substr", S, H,
  "string s.substr(size_t pos, size_t len = npos);",
  r'''std::string s = "hello";
std::string t = s.substr(1, 3);   // "ell"  (start, LENGTH)''',
  "O(len)", "Second argument is a length, not an end index. Throws std::out_of_range if pos > size().")
E("find", S, H,
  "size_t s.find(const string& sub, size_t pos = 0);\nsize_t s.find(char c, size_t pos = 0);",
  r'''std::string s = "hello";
size_t i = s.find("ll");   // 2
if (s.find('z') == std::string::npos) { /* absent */ }''',
  "O(n*m)", "Returns std::string::npos if not found. Store it in size_t, never int.")
E("rfind", S, H,
  "size_t s.rfind(const string& sub);\nsize_t s.rfind(char c);",
  r'''std::string s = "a/b/c";
size_t i = s.rfind('/');   // 3 (last occurrence)''',
  "O(n*m)", "Searches from the end. Returns npos if not found.")
E("npos", S, H,
  "static const size_t std::string::npos;",
  r'''std::string s = "abc";
bool missing = (s.find('z') == std::string::npos);   // true''',
  "", "Equals (size_t)-1, the 'not found' value of find/rfind.")
E("append / +=", S, H,
  "string& s.append(const string& t);\nstring& s += t;   // t may be string, const char*, or char",
  r'''std::string s = "ab";
s += "cd";
s.append(2, '!');   // s = "abcd!!"''',
  "amortised O(len)", "s + 'x' + 'y' fails if the left side is a const char*: start from a std::string.")
E("push_back", S, H,
  "void s.push_back(char c);",
  r'''std::string s = "ab";
s.push_back('c');   // "abc"''',
  "amortised O(1)", "Takes a char, not a string.")
E("compare / ==", S, H,
  "int s.compare(const string& t);\nbool s == t;   // also <, >, !=",
  r'''std::string a = "abc", b = "abd";
bool eq = (a == b);          // false
int c = a.compare(b);        // < 0''',
  "O(n)", "compare returns <0, 0, >0 (not -1/1). == compares content, not addresses.")
E("c_str", S, H,
  "const char* s.c_str();",
  r'''std::string s = "hi";
const char* p = s.c_str();   // for C functions, e.g. std::puts(p)''',
  "O(1)", "Pointer dies when s changes or is destroyed. Read-only.")
E("to_string", S, H,
  "string std::to_string(int / long / long long / unsigned / float / double v);",
  r'''std::string a = std::to_string(42);     // "42"
std::string b = std::to_string(3.5);    // "3.500000"''',
  "", "Floating point always gives 6 decimals; use ostringstream + setprecision for control.")
E("stoi", S, H,
  "int std::stoi(const string& s, size_t* pos = nullptr, int base = 10);\nlong std::stol(...);   long long std::stoll(...);",
  r'''int a = std::stoi("123");     // 123
int b = std::stoi("ff", nullptr, 16);   // 255''',
  "O(n)", "Throws std::invalid_argument (no digits) or std::out_of_range. Stops silently at the first non-digit: stoi(\"12ab\") is 12.")
E("stod", S, H,
  "double std::stod(const string& s, size_t* pos = nullptr);\nfloat std::stof(...);",
  r'''double d = std::stod("3.14");   // 3.14''',
  "O(n)", "Throws std::invalid_argument / std::out_of_range like stoi.")
E("getline", S, "<string>, <iostream>",
  "istream& std::getline(istream& in, string& s);\nistream& std::getline(istream& in, string& s, char delim);",
  r'''std::string line;
std::getline(std::cin, line);              // whole line, '\n' dropped
while (std::getline(std::cin, line)) { }   // read until EOF''',
  "O(n)", "After 'cin >> x' a '\\n' stays in the buffer: call std::cin.ignore() (or getline once) before the next getline.")
E("string(n, c)", S, H,
  "std::string(size_t n, char c);",
  r'''std::string s(3, 'x');   // "xxx"
std::string t(5, '-');   // "-----"''',
  "O(n)", "Argument order is (count, char). std::string(\"x\", 3) is a different (wrong) constructor.")

# ---------------------------------------------------------------- algorithm
S = "algorithm"
H = "<algorithm>"
E("sort", S, "<algorithm>, <functional>",
  "void std::sort(It first, It last);\nvoid std::sort(It first, It last, Compare comp);",
  r'''std::vector<int> v{3,1,2};
std::sort(v.begin(), v.end());                          // {1,2,3}
std::sort(v.begin(), v.end(), std::greater<int>());     // {3,2,1}''',
  "O(n log n)", "Needs random-access iterators: not std::list (use l.sort()). comp must be a strict order (< or >, never <= or >=), otherwise UB/crash.")
E("stable_sort", S, H,
  "void std::stable_sort(It first, It last[, Compare comp]);",
  r'''std::vector<std::pair<int,int>> v{{2,1},{1,2},{2,0}};
std::stable_sort(v.begin(), v.end(), [](auto& a, auto& b){ return a.first < b.first; });''',
  "O(n log n)", "Keeps the original order of equal elements.")
E("sort with lambda", S, H,
  "std::sort(first, last, [](const T& a, const T& b) { return <a goes before b>; });",
  r'''std::vector<std::pair<int,int>> v{{1,5},{2,3}};
std::sort(v.begin(), v.end(), [](const auto& a, const auto& b) { return a.second < b.second; });''',
  "O(n log n)", "comp(a,b) returns true if a must come BEFORE b (a is better/smaller). Ascending uses <.")
E("reverse", S, H,
  "void std::reverse(It first, It last);",
  r'''std::vector<int> v{1,2,3};
std::reverse(v.begin(), v.end());   // {3,2,1}''',
  "O(n)", "In place; returns nothing.")
E("find", S, H,
  "It std::find(It first, It last, const T& val);",
  r'''std::vector<int> v{4,5,6};
auto it = std::find(v.begin(), v.end(), 5);
if (it != v.end()) { int idx = it - v.begin(); }   // idx = 1''',
  "O(n)", "Returns last (v.end()) if not found. Index = it - v.begin().")
E("find_if", S, H,
  "It std::find_if(It first, It last, Pred p);",
  r'''std::vector<int> v{1,4,6};
auto it = std::find_if(v.begin(), v.end(), [](int x){ return x > 3; });   // points to 4''',
  "O(n)", "Returns last if none matches.")
E("count", S, H,
  "ptrdiff_t std::count(It first, It last, const T& val);",
  r'''std::vector<int> v{1,2,2,3};
auto c = std::count(v.begin(), v.end(), 2);   // 2''',
  "O(n)", "")
E("count_if", S, H,
  "ptrdiff_t std::count_if(It first, It last, Pred p);",
  r'''std::vector<int> v{1,2,3,4};
auto c = std::count_if(v.begin(), v.end(), [](int x){ return x % 2 == 0; });   // 2''',
  "O(n)", "")
E("min_element", S, H,
  "It std::min_element(It first, It last[, Compare comp]);",
  r'''std::vector<int> v{3,1,2};
auto it = std::min_element(v.begin(), v.end());
int m = *it, idx = it - v.begin();   // 1, 1''',
  "O(n)", "Returns an ITERATOR (dereference for the value). Returns last if empty: dereferencing then is UB. First of equal minima.")
E("max_element", S, H,
  "It std::max_element(It first, It last[, Compare comp]);",
  r'''std::vector<int> v{3,1,2};
auto it = std::max_element(v.begin(), v.end());
int m = *it, idx = it - v.begin();   // 3, 0''',
  "O(n)", "Returns an ITERATOR. Returns last if empty. First of equal maxima. comp(a,b) true means a < b.")
E("minmax_element", S, H,
  "pair<It,It> std::minmax_element(It first, It last[, Compare comp]);",
  r'''std::vector<int> v{3,1,2};
auto [lo, hi] = std::minmax_element(v.begin(), v.end());
int mn = *lo, mx = *hi;   // 1, 3''',
  "O(n)", "One pass; returns {min iterator, max iterator}. For ties, min is the first and max is the LAST.")
E("min", S, H,
  "const T& std::min(const T& a, const T& b[, Compare comp]);\nT std::min(initializer_list<T> il);",
  r'''int a = std::min(3, 5);        // 3
int b = std::min({4, 1, 7});   // 1''',
  "O(1)", "Both arguments must have the SAME type: std::min(1, 2.5) does not compile. Use std::min<double>(1, 2.5).")
E("max", S, H,
  "const T& std::max(const T& a, const T& b[, Compare comp]);\nT std::max(initializer_list<T> il);",
  r'''int a = std::max(3, 5);        // 5
int b = std::max({4, 1, 7});   // 7''',
  "O(1)", "Both arguments must have the SAME type. Returns a reference: do not keep it bound to a temporary.")
E("clamp", S, H,
  "const T& std::clamp(const T& v, const T& lo, const T& hi);",
  r'''int x = std::clamp(15, 0, 10);   // 10
double y = std::clamp(-1.5, 0.0, 1.0);   // 0.0''',
  "O(1)", "C++17. Argument order is (value, low, high). UB if lo > hi.")
E("swap", S, "<utility>",
  "void std::swap(T& a, T& b);\nvoid std::iter_swap(It a, It b);",
  r'''std::vector<int> v{1,2,3};
std::swap(v[0], v[2]);   // v = {3,2,1}''',
  "O(1)", "Works on any two values of the same type. Also v.swap(w) swaps whole containers in O(1).")
E("fill", S, H,
  "void std::fill(It first, It last, const T& val);",
  r'''std::vector<int> v(5);
std::fill(v.begin(), v.end(), 7);   // {7,7,7,7,7}''',
  "O(n)", "")
E("copy", S, "<algorithm>, <iterator>",
  "OutIt std::copy(It first, It last, OutIt dest);",
  r'''std::vector<int> a{1,2,3}, b;
std::copy(a.begin(), a.end(), std::back_inserter(b));   // b = {1,2,3}''',
  "O(n)", "dest must already have room: otherwise use std::back_inserter(dst) or resize first. Never copy into an empty vector's begin().")
E("transform", S, H,
  "OutIt std::transform(It first, It last, OutIt dest, UnaryOp f);\nOutIt std::transform(It1 f1, It1 l1, It2 f2, OutIt dest, BinaryOp f);",
  r'''std::vector<int> a{1,2,3};
std::transform(a.begin(), a.end(), a.begin(), [](int x){ return x * x; });   // {1,4,9}''',
  "O(n)", "dest may equal first (in place). dest must have room.")
E("remove (erase-remove idiom)", S, H,
  "It std::remove(It first, It last, const T& val);\nv.erase(std::remove(v.begin(), v.end(), val), v.end());",
  r'''std::vector<int> v{1,2,2,3};
v.erase(std::remove(v.begin(), v.end(), 2), v.end());   // v = {1,3}''',
  "O(n)", "std::remove alone only shuffles elements and returns the new logical end; the vector keeps its size until you erase(it, end).")
E("remove_if", S, H,
  "It std::remove_if(It first, It last, Pred p);\nv.erase(std::remove_if(v.begin(), v.end(), p), v.end());",
  r'''std::vector<int> v{1,2,3,4};
v.erase(std::remove_if(v.begin(), v.end(), [](int x){ return x % 2 == 0; }), v.end());   // {1,3}''',
  "O(n)", "Same as remove: needs the .erase(...) call to actually shrink.")
E("unique", S, H,
  "It std::unique(It first, It last[, BinaryPred p]);",
  r'''std::vector<int> v{3,1,3,2,1};
std::sort(v.begin(), v.end());
v.erase(std::unique(v.begin(), v.end()), v.end());   // {1,2,3}''',
  "O(n)", "Removes only CONSECUTIVE duplicates: sort first. Like remove, it needs .erase(...) afterwards.")
E("any_of", S, H,
  "bool std::any_of(It first, It last, Pred p);",
  r'''std::vector<int> v{1,2,3};
bool b = std::any_of(v.begin(), v.end(), [](int x){ return x > 2; });   // true''',
  "O(n)", "false on an empty range.")
E("all_of", S, H,
  "bool std::all_of(It first, It last, Pred p);",
  r'''std::vector<int> v{1,2,3};
bool b = std::all_of(v.begin(), v.end(), [](int x){ return x > 0; });   // true''',
  "O(n)", "true on an empty range.")
E("none_of", S, H,
  "bool std::none_of(It first, It last, Pred p);",
  r'''std::vector<int> v{1,2,3};
bool b = std::none_of(v.begin(), v.end(), [](int x){ return x < 0; });   // true''',
  "O(n)", "true on an empty range.")
E("lower_bound", S, H,
  "It std::lower_bound(It first, It last, const T& val[, Compare comp]);",
  r'''std::vector<int> v{1,3,3,5};
auto it = std::lower_bound(v.begin(), v.end(), 3);
int idx = it - v.begin();   // 1 (first element >= 3)''',
  "O(log n)", "Range MUST be sorted. First element >= val, or last if none. For std::set / std::map use the member function.")
E("upper_bound", S, H,
  "It std::upper_bound(It first, It last, const T& val[, Compare comp]);",
  r'''std::vector<int> v{1,3,3,5};
auto it = std::upper_bound(v.begin(), v.end(), 3);
int idx = it - v.begin();   // 3 (first element > 3)''',
  "O(log n)", "Range MUST be sorted. First element > val, or last. Count of val = upper_bound - lower_bound.")
E("binary_search", S, H,
  "bool std::binary_search(It first, It last, const T& val[, Compare comp]);",
  r'''std::vector<int> v{1,3,5};
bool found = std::binary_search(v.begin(), v.end(), 3);   // true''',
  "O(log n)", "Range MUST be sorted. Returns bool only, not a position (use lower_bound for that).")
E("next_permutation", S, H,
  "bool std::next_permutation(It first, It last[, Compare comp]);",
  r'''std::vector<int> v{1,2,3};
do { /* use v */ } while (std::next_permutation(v.begin(), v.end()));''',
  "O(n)", "Sort first to visit ALL permutations. Returns false (and resets to sorted) after the last one.")
E("shuffle", S, "<algorithm>, <random>",
  "void std::shuffle(It first, It last, URBG&& g);",
  r'''std::vector<int> v{1,2,3,4};
std::mt19937 rng(42);
std::shuffle(v.begin(), v.end(), rng);''',
  "O(n)", "Needs a <random> engine as 3rd argument. std::random_shuffle was removed in C++17.")
E("for_each", S, H,
  "Fn std::for_each(It first, It last, Fn f);",
  r'''std::vector<int> v{1,2,3};
std::for_each(v.begin(), v.end(), [](int& x){ x *= 2; });   // {2,4,6}''',
  "O(n)", "Take the element by reference (int&) if you want to modify it.")

# ---------------------------------------------------------------- numeric
S = "numeric"
H = "<numeric>"
E("accumulate", S, H,
  "T std::accumulate(It first, It last, T init[, BinaryOp op]);",
  r'''std::vector<double> v{1.5, 2.0};
double s = std::accumulate(v.begin(), v.end(), 0.0);   // 3.5''',
  "O(n)", "Result type = type of init: accumulate(..., 0) on doubles truncates to int; use 0.0 (or 0LL to avoid int overflow).")
E("iota", S, H,
  "void std::iota(It first, It last, T start);",
  r'''std::vector<int> v(5);
std::iota(v.begin(), v.end(), 0);   // {0,1,2,3,4}''',
  "O(n)", "Fills with start, start+1, ... The vector must already have its size.")
E("partial_sum", S, H,
  "OutIt std::partial_sum(It first, It last, OutIt dest[, BinaryOp op]);",
  r'''std::vector<int> v{1,2,3}, out(3);
std::partial_sum(v.begin(), v.end(), out.begin());   // out = {1,3,6}''',
  "O(n)", "Prefix sums. dest may equal first (in place).")
E("inner_product", S, H,
  "T std::inner_product(It1 f1, It1 l1, It2 f2, T init);",
  r'''std::vector<int> a{1,2,3}, b{4,5,6};
int dot = std::inner_product(a.begin(), a.end(), b.begin(), 0);   // 32''',
  "O(n)", "Dot product. Second range is given by its start only and must be as long as the first.")

# ---------------------------------------------------------------- utility / tuple
S = "utility / tuple"
E("pair / make_pair", S, "<utility>",
  "std::pair<A,B> p(a, b);   std::pair<A,B> p{a, b};\nstd::pair<A,B> std::make_pair(a, b);\np.first   p.second",
  r'''std::pair<int,std::string> p = std::make_pair(1, std::string("x"));
int a = p.first;
p.second = "y";''',
  "O(1)", "Comparison is lexicographic (first, then second), so sort/set/map work on pairs.")
E("tuple / make_tuple", S, "<tuple>",
  "std::tuple<A,B,C> t(a, b, c);\nstd::tuple<A,B,C> std::make_tuple(a, b, c);",
  r'''auto t = std::make_tuple(1, 2.5, std::string("x"));
std::tuple<int,double> u{3, 4.5};''',
  "O(1)", "Access with std::get<I>(t), not t.first.")
E("tie", S, "<tuple>",
  "tuple<A&,B&> std::tie(a, b);",
  r'''int a, b;
std::tie(a, b) = std::make_pair(1, 2);   // a = 1, b = 2
bool less = std::tie(a, b) < std::tie(b, a);   // lexicographic compare''',
  "O(1)", "Unpacks into EXISTING variables (structured bindings declare new ones). Use std::ignore to skip a field.")
E("get", S, "<tuple>, <utility>",
  "T& std::get<I>(tuple_or_pair& t);\nT& std::get<Type>(tuple_or_pair& t);",
  r'''auto t = std::make_tuple(1, 2.5, std::string("x"));
double d = std::get<1>(t);       // 2.5
std::get<0>(t) = 7;''',
  "O(1)", "Index must be a compile-time constant. By type only if that type appears once.")
E("structured binding", S, "<utility>",
  "auto [a, b] = p;\nconst auto& [a, b] = p;   // pair, tuple, struct, array",
  r'''std::pair<int,double> p{1, 2.5};
auto [i, d] = p;   // i = 1, d = 2.5''',
  "", "C++17. Declares new variables; auto& binds by reference so changes write through.")
E("move", S, "<utility>",
  "T&& std::move(T& x);",
  r'''std::string a = "hello";
std::string b = std::move(a);   // b = "hello", a is valid but unspecified (usually "")''',
  "O(1)", "Only casts to an rvalue; the move happens in the receiving constructor/assignment. Do not use the moved-from object (except to assign/destroy).")
E("swap", S, "<utility>",
  "void a.swap(other);   // member of every container\nvoid std::swap(a, b);",
  r'''std::vector<int> a{1,2}, b{3};
a.swap(b);   // a = {3}, b = {1,2}, O(1)''',
  "O(1)", "Container swap exchanges internals, no element copies.")

# ---------------------------------------------------------------- memory
S = "memory"
H = "<memory>"
E("make_unique", S, H,
  "std::unique_ptr<T> std::make_unique<T>(args...);",
  r'''auto p = std::make_unique<int>(5);
int x = *p;   // 5''',
  "O(1)", "Sole owner: cannot be copied, only moved (std::move(p)). Freed automatically.")
E("make_shared", S, H,
  "std::shared_ptr<T> std::make_shared<T>(args...);",
  r'''auto a = std::make_shared<int>(1);
auto b = a;                  // shared ownership
long n = a.use_count();      // 2''',
  "O(1)", "Last owner frees. Cycles of shared_ptr leak: break them with std::weak_ptr.")
E("unique_ptr::get", S, H,
  "T* p.get();",
  r'''auto p = std::make_unique<int>(5);
int* raw = p.get();   // raw non-owning pointer''',
  "O(1)", "Does NOT give up ownership: never delete the raw pointer.")
E("unique_ptr::reset", S, H,
  "void p.reset();\nvoid p.reset(T* q);",
  r'''auto p = std::make_unique<int>(5);
p.reset();                 // frees; p == nullptr
p.reset(new int(7));       // takes ownership of new object''',
  "O(1)", "Deletes the old object, then owns q (or nothing).")

# ---------------------------------------------------------------- random
S = "random"
H = "<random>"
E("mt19937 (seeding)", S, H,
  "std::mt19937 rng(seed);\nstd::mt19937 rng(std::random_device{}());",
  r'''std::mt19937 fixed(42);                         // reproducible
std::mt19937 rng(std::random_device{}());       // different each run
unsigned x = rng();''',
  "O(1)", "Fixed seed gives the same sequence every run (good for tests). Create ONE engine and reuse it; do not re-seed in a loop.")
E("uniform_int_distribution", S, H,
  "std::uniform_int_distribution<int> d(a, b);\nint x = d(rng);",
  r'''std::mt19937 rng(42);
std::uniform_int_distribution<int> d(1, 6);
int roll = d(rng);   // 1..6''',
  "O(1)", "Both ends INCLUSIVE: (a, b) gives a..b.")
E("uniform_real_distribution", S, H,
  "std::uniform_real_distribution<double> d(a, b);\ndouble x = d(rng);",
  r'''std::mt19937 rng(42);
std::uniform_real_distribution<double> d(0.0, 1.0);
double x = d(rng);   // [0, 1)''',
  "O(1)", "Half-open [a, b).")
E("normal_distribution", S, H,
  "std::normal_distribution<double> d(mean, stddev);\ndouble x = d(rng);",
  r'''std::mt19937 rng(42);
std::normal_distribution<double> noise(0.0, 0.1);
double x = noise(rng);''',
  "O(1)", "Second parameter is the standard deviation, not the variance.")
E("bernoulli_distribution", S, H,
  "std::bernoulli_distribution d(p);\nbool b = d(rng);",
  r'''std::mt19937 rng(42);
std::bernoulli_distribution coin(0.5);
bool heads = coin(rng);''',
  "O(1)", "p is the probability of true.")

# ---------------------------------------------------------------- chrono
S = "chrono"
E("steady_clock::now", S, "<chrono>",
  "time_point std::chrono::steady_clock::now();",
  r'''auto t0 = std::chrono::steady_clock::now();
auto t1 = std::chrono::steady_clock::now();
auto dt = t1 - t0;   // a duration''',
  "O(1)", "Use steady_clock to measure intervals (system_clock can jump).")
E("duration_cast<milliseconds>", S, "<chrono>",
  "auto n = std::chrono::duration_cast<std::chrono::milliseconds>(dt).count();",
  r'''auto t0 = std::chrono::steady_clock::now();
auto t1 = std::chrono::steady_clock::now();
auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(t1 - t0).count();''',
  "O(1)", "Truncates, does not round. .count() gives a plain integer. Swap milliseconds for microseconds / seconds as needed.")
E("duration<double>", S, "<chrono>",
  "double std::chrono::duration<double>(dt).count();",
  r'''auto t0 = std::chrono::steady_clock::now();
auto t1 = std::chrono::steady_clock::now();
double sec = std::chrono::duration<double>(t1 - t0).count();''',
  "O(1)", "Seconds as a double, no cast needed.")
E("this_thread::sleep_for", S, "<thread>, <chrono>",
  "void std::this_thread::sleep_for(duration);",
  r'''std::this_thread::sleep_for(std::chrono::milliseconds(100));''',
  "", "Needs #include <thread> (and -pthread when linking on some setups).")

# ---------------------------------------------------------------- cmath
S = "cmath"
H = "<cmath>"
E("sqrt", S, H,
  "double std::sqrt(double x);",
  r'''double r = std::sqrt(16.0);   // 4.0''',
  "O(1)", "Negative input gives NaN.")
E("pow", S, H,
  "double std::pow(double base, double exp);",
  r'''double r = std::pow(2.0, 10);   // 1024.0''',
  "O(1)", "Returns double even for int arguments (may be 1023.9999 -> truncates wrongly when cast to int). Use std::round, or multiply for small integer powers.")
E("abs / fabs", S, "<cmath>, <cstdlib>",
  "int std::abs(int x);   double std::abs(double x);\ndouble std::fabs(double x);",
  r'''int a = std::abs(-3);         // 3
double b = std::fabs(-2.5);   // 2.5''',
  "O(1)", "Always write std::abs: plain abs() may pick the int version and truncate a double.")
E("hypot", S, H,
  "double std::hypot(double x, double y);",
  r'''double d = std::hypot(3.0, 4.0);   // 5.0''',
  "O(1)", "sqrt(x*x + y*y) without overflow.")
E("atan2", S, H,
  "double std::atan2(double y, double x);",
  r'''double th = std::atan2(1.0, 1.0);   // 0.785398 (pi/4)''',
  "O(1)", "Argument order is (y, x). Result is radians in [-pi, pi].")
E("sin / cos / tan", S, H,
  "double std::sin(double rad);   double std::cos(double rad);   double std::tan(double rad);",
  r'''double s = std::sin(3.14159265358979 / 2);   // 1.0''',
  "O(1)", "Angles are in RADIANS. deg * pi / 180.")
E("pi constant", S, H,
  "const double PI = std::acos(-1.0);",
  r'''const double PI = std::acos(-1.0);
double rad = 90.0 * PI / 180.0;''',
  "", "There is no std::pi in C++17 (std::numbers::pi is C++20). M_PI works with g++ on Linux but is not standard.")
E("floor / ceil / round", S, H,
  "double std::floor(double x);\ndouble std::ceil(double x);\ndouble std::round(double x);\nlong std::lround(double x);",
  r'''double a = std::floor(2.7);   // 2.0
double b = std::ceil(2.1);    // 3.0
long c = std::lround(2.5);    // 3''',
  "O(1)", "All return double (except lround): cast with static_cast<int>. round rounds halves away from zero.")
E("fmod", S, H,
  "double std::fmod(double x, double y);",
  r'''double r = std::fmod(7.5, 2.0);   // 1.5''',
  "O(1)", "Remainder with the sign of x. Use % only for integers.")
E("isnan", S, H,
  "bool std::isnan(double x);   bool std::isinf(double x);",
  r'''double x = std::sqrt(-1.0);
bool bad = std::isnan(x);   // true''',
  "O(1)", "x == x is false for NaN; never compare NaN with ==.")

# ---------------------------------------------------------------- iostream / sstream
S = "iostream / sstream"
E("cout with setprecision", S, "<iostream>, <iomanip>",
  "std::cout << std::fixed << std::setprecision(n) << x;\nstd::cout << std::setw(n) << x;",
  r'''double x = 3.14159;
std::cout << std::fixed << std::setprecision(2) << x << "\n";   // 3.14''',
  "", "With std::fixed, n counts digits AFTER the point; without it, n counts significant digits. Both stick to the stream until changed. Prefer \"\\n\" to std::endl (which flushes).")
E("cin", S, "<iostream>",
  "std::cin >> a >> b;\nwhile (std::cin >> x) { ... }",
  r'''int a, b;
std::cin >> a >> b;
double x;
while (std::cin >> x) { }   // until EOF or bad input''',
  "", "Skips whitespace. Leaves the newline in the buffer (matters before getline). The stream converts to false on failure.")
E("fast IO", S, "<iostream>",
  "std::ios::sync_with_stdio(false);\nstd::cin.tie(nullptr);",
  r'''std::ios::sync_with_stdio(false);
std::cin.tie(nullptr);''',
  "", "Put at the top of main. Afterwards do not mix cin/cout with scanf/printf.")
E("istringstream split", S, "<sstream>, <string>, <vector>",
  "std::istringstream iss(str);\niss >> word;                  // split on whitespace\nstd::getline(iss, tok, ',');   // split on a delimiter",
  r'''std::istringstream iss("1,2,3");
std::string tok;
std::vector<int> out;
while (std::getline(iss, tok, ',')) out.push_back(std::stoi(tok));   // {1,2,3}''',
  "O(n)", "For whitespace-separated words use 'while (iss >> tok)'.")
E("ostringstream", S, "<sstream>",
  "std::ostringstream os;\nos << ...;\nstd::string s = os.str();",
  r'''std::ostringstream os;
os << "x=" << 3 << ", y=" << 4.5;
std::string s = os.str();   // "x=3, y=4.5"''',
  "O(n)", "Builds a string with the same << formatting as cout (setprecision works).")

# ---------------------------------------------------------------- limits / misc
S = "limits / misc"
E("numeric_limits<int>::max()", S, "<limits>",
  "T std::numeric_limits<T>::max();   T std::numeric_limits<T>::min();   T std::numeric_limits<T>::lowest();",
  r'''int big = std::numeric_limits<int>::max();           // 2147483647
double neg = std::numeric_limits<double>::lowest();''',
  "O(1)", "For floating point, min() is the smallest POSITIVE value; use lowest() for the most negative.")
E("numeric_limits<double>::infinity / epsilon", S, "<limits>",
  "double std::numeric_limits<double>::infinity();\ndouble std::numeric_limits<double>::epsilon();",
  r'''double inf = std::numeric_limits<double>::infinity();
double eps = std::numeric_limits<double>::epsilon();''',
  "O(1)", "Compare doubles with std::fabs(a - b) < eps-ish, not ==.")
E("INT_MAX", S, "<climits>",
  "INT_MAX   INT_MIN   LLONG_MAX   UINT_MAX",
  r'''int big = INT_MAX;                     // 2147483647
long long m = LLONG_MAX;''',
  "", "INT_MAX + 1 overflows (UB). Using INT_MAX as 'infinity' in sums can overflow: prefer INT_MAX / 2 or long long.")
E("size (std::size)", S, "<iterator>",
  "size_t std::size(const C& c);",
  r'''int a[5] = {1,2,3,4,5};
size_t n = std::size(a);   // 5''',
  "O(1)", "C++17. Works on C arrays and containers. sizeof(a) would be the byte count.")
E("static_cast", S, "(built-in)",
  "T static_cast<T>(expr)",
  r'''int n = 7;
double r = static_cast<double>(n) / 2;   // 3.5
int i = static_cast<int>(3.9);           // 3 (truncates)''',
  "", "n / 2 with ints is integer division: cast one operand first.")
E("std::function declaration", S, "<functional>",
  "std::function<ReturnType(ArgTypes...)> f = callable;",
  r'''std::function<int(int,int)> f = [](int a, int b) { return a + b; };
int r = f(2, 3);   // 5''',
  "", "Holds lambdas, function pointers and functors. Slightly slower than auto for a lambda.")
E("lambda syntax", S, "(built-in)",
  "[capture](params) -> ret { body }\n[=] copy all   [&] reference all   [x, &y] mixed",
  r'''int k = 10;
auto add = [k](int x) { return x + k; };
int r = add(5);   // 15''',
  "", "A by-value capture is const unless the lambda is marked mutable. Return type is deduced; add -> double if branches return different types.")
