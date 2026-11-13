// dbg.h: print debugging.   #include "dbg.h"   then   dbg(x, v, m.size());
// prints to stderr:   [grid.cpp:42] x = 3 | v = {1, 2} | m.size() = 2
// Numbers, strings, pairs, tuples and any container, nested too (vector<pair<int, set<int>>> ...).
// Silence every call without deleting them: compile with -DDBG_OFF.
#pragma once
#include <cstddef>
#include <iostream>
#include <iterator>
#include <string>
#include <string_view>
#include <tuple>
#include <type_traits>
#include <utility>
#include <vector>

namespace dbg_detail {

template <class T, class = void> struct iterable : std::false_type {};
template <class T>
struct iterable<T, std::void_t<decltype(std::begin(std::declval<const T &>())),
                               decltype(std::end(std::declval<const T &>()))>> : std::true_type {};

template <class T, class = void> struct streamable : std::false_type {};
template <class T>
struct streamable<T, std::void_t<decltype(std::declval<std::ostream &>() << std::declval<const T &>())>>
    : std::true_type {};

template <class T> void show(std::ostream &os, const T &x);

template <class A, class B> void show(std::ostream &os, const std::pair<A, B> &p)
{
    os << '(';
    show(os, p.first);
    os << ", ";
    show(os, p.second);
    os << ')';
}

template <class... Ts> void show(std::ostream &os, const std::tuple<Ts...> &t)
{
    os << '(';
    std::apply([&os](const auto &...xs) {
        std::size_t i = 0;
        ((os << (i++ ? ", " : ""), show(os, xs)), ...);
    }, t);
    os << ')';
}

template <class T> void show(std::ostream &os, const T &x)
{
    if constexpr (std::is_same_v<T, std::string> || std::is_same_v<T, std::string_view>)
        os << '"' << x << '"';
    else if constexpr (std::is_same_v<T, bool>)
        os << (x ? "true" : "false");
    else if constexpr (streamable<T>::value)
        os << x;
    else if constexpr (iterable<T>::value) {
        os << '{';
        bool first = true;
        for (const auto &e : x) {
            if (!first) os << ", ";
            first = false;
            show(os, e);
        }
        os << '}';
    }
    else
        os << "<not printable>";
}

// "a, f(b, c), v[1]" -> {"a", "f(b, c)", "v[1]"}: split on top-level commas only
inline std::vector<std::string> names(std::string_view s)
{
    std::vector<std::string> out(1);
    int depth = 0;
    bool quoted = false;
    for (char c : s) {
        if (c == '"') quoted = !quoted;
        if (!quoted) {
            if (c == '(' || c == '[' || c == '{') ++depth;
            else if (c == ')' || c == ']' || c == '}') --depth;
            else if (c == ',' && depth == 0) { out.emplace_back(); continue; }
        }
        if (!(c == ' ' && out.back().empty())) out.back() += c;
    }
    return out;
}

template <class... Ts> void print(const char *file, int line, const char *expr, const Ts &...xs)
{
    std::string_view f(file);
    if (auto slash = f.find_last_of("/\\"); slash != std::string_view::npos) f.remove_prefix(slash + 1);
    const auto n = names(expr);
    std::size_t i = 0;
    std::cerr << '[' << f << ':' << line << "] ";
    ((std::cerr << (i ? " | " : "") << (i < n.size() ? n[i] : std::string("?")) << " = ", show(std::cerr, xs), ++i), ...);
    std::cerr << std::endl;
}

template <class... Ts> int sink(const Ts &...);   // never defined: only used unevaluated

} // namespace dbg_detail

#ifdef DBG_OFF   // arguments are not evaluated, but still count as used (no unused-variable warnings)
#define dbg(...) ((void)sizeof(::dbg_detail::sink(__VA_ARGS__)))
#else
#define dbg(...) ::dbg_detail::print(__FILE__, __LINE__, #__VA_ARGS__, __VA_ARGS__)
#endif
