// recursion.cpp - classic recursion patterns: Hanoi, permutations, subsets, memoization.
// Build: g++ -std=c++17 -Wall -Wextra -O2 recursion.cpp -o recursion
#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

// Towers of Hanoi: move n discs from 'from' to 'to' using 'via'.
// Move n-1 to via, move the big one, move n-1 from via onto it. 2^n - 1 moves.
void hanoi(int n, char from, char to, char via, long long &moves, bool print)
{
    if(n == 0)
        return;
    hanoi(n - 1, from, via, to, moves, print);
    ++moves;
    if(print)
        std::cout << "  move disc " << n << " " << from << " -> " << to << "\n";
    hanoi(n - 1, via, to, from, moves, print);
}

// Permutations by swapping (in place, with undo = backtracking pattern).
// ADAPT: replace the print by whatever you do with a full permutation.
void permute(std::vector<int> &a, size_t k, long long &count, bool print)
{
    if(k == a.size())
    {
        ++count;
        if(print)
        {
            std::cout << " ";
            for(int x : a)
                std::cout << ' ' << x;
            std::cout << "\n";
        }
        return;
    }
    for(size_t i = k; i < a.size(); ++i)
    {
        std::swap(a[k], a[i]);          // set
        permute(a, k + 1, count, print);
        std::swap(a[k], a[i]);          // cancel
    }
}

// Permutations in lexicographic order using the standard library.
long long permuteStl(std::vector<int> a)
{
    std::sort(a.begin(), a.end());      // next_permutation needs sorted input to see all
    long long n = 0;
    do
    {
        ++n;
    } while(std::next_permutation(a.begin(), a.end()));
    return n;
}

// Subsets (power set): for each item either skip it or take it.
void subsets(const std::vector<int> &items, size_t i, std::vector<int> &current,
             std::vector<std::vector<int>> &out)
{
    if(i == items.size())
    {
        out.push_back(current);
        return;
    }
    subsets(items, i + 1, current, out);        // skip item i
    current.push_back(items[i]);                // take item i   (set)
    subsets(items, i + 1, current, out);
    current.pop_back();                         //               (cancel)
}

// Same with a bitmask: bit j of mask says "item j is in".
std::vector<std::vector<int>> subsetsMask(const std::vector<int> &items)
{
    std::vector<std::vector<int>> out;
    const unsigned int total = 1u << items.size();   // fine up to ~25 items
    for(unsigned int mask = 0; mask < total; ++mask)
    {
        std::vector<int> s;
        for(size_t j = 0; j < items.size(); ++j)
            if(mask & (1u << j))
                s.push_back(items[j]);
        out.push_back(s);
    }
    return out;
}

// Subset-sum: is there a subset of 'items' adding up to 'target'? (with early exit)
bool subsetSum(const std::vector<int> &items, size_t i, int target)
{
    if(target == 0)
        return true;
    if(i == items.size() || target < 0)
        return false;
    return subsetSum(items, i + 1, target - items[i]) || subsetSum(items, i + 1, target);
}

// Memoization
// Fibonacci: naive is exponential, memoised is linear.
long long fibNaive(int n)
{
    if(n < 2)
        return n;
    return fibNaive(n - 1) + fibNaive(n - 2);
}

long long fibMemo(int n, std::unordered_map<int, long long> &memo)
{
    if(n < 2)
        return n;
    auto it = memo.find(n);
    if(it != memo.end())
        return it->second;
    const long long r = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    memo[n] = r;                                // store before returning
    return r;
}

// Number of ways to make 'amount' with coins (order does not matter), memo on (amount, idx).
// ADAPT: key = every parameter that changes between calls.
long long ways(int amount, size_t idx, const std::vector<int> &coins,
               std::map<std::pair<int, size_t>, long long> &memo)
{
    if(amount == 0)
        return 1;
    if(amount < 0 || idx == coins.size())
        return 0;
    const std::pair<int, size_t> key(amount, idx);
    auto it = memo.find(key);
    if(it != memo.end())
        return it->second;
    const long long r = ways(amount - coins[idx], idx, coins, memo)   // use coin idx again
                      + ways(amount, idx + 1, coins, memo);           // move on to next coin
    memo[key] = r;
    return r;
}

// Bottom-up dynamic programming, same result.
long long fibBottomUp(int n)
{
    if(n < 2)
        return n;
    long long a = 0, b = 1;
    for(int i = 2; i <= n; ++i)
    {
        const long long c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main()
{
    std::cout << "Hanoi with 3 discs:\n";
    long long moves = 0;
    hanoi(3, 'A', 'C', 'B', moves, true);
    std::cout << "3 discs -> " << moves << " moves\n";
    moves = 0;
    hanoi(16, 'A', 'C', 'B', moves, false);
    std::cout << "16 discs -> " << moves << " moves (2^16-1 = 65535)\n";

    std::cout << "Permutations of {1,2,3}:\n";
    std::vector<int> a{1, 2, 3};
    long long count = 0;
    permute(a, 0, count, true);
    std::vector<int> b{1, 2, 3, 4, 5, 6, 7};
    count = 0;
    permute(b, 0, count, false);
    std::cout << "7 elements -> " << count << " permutations (5040), next_permutation says "
              << permuteStl(b) << "\n";

    const std::vector<int> items{1, 2, 3};
    std::vector<std::vector<int>> all;
    std::vector<int> cur;
    subsets(items, 0, cur, all);
    std::cout << "subsets of {1,2,3}: " << all.size() << " (mask version: "
              << subsetsMask(items).size() << ")\n";
    for(const auto &s : all)
    {
        std::cout << "  {";
        for(size_t i = 0; i < s.size(); ++i)
            std::cout << (i ? "," : "") << s[i];
        std::cout << "}\n";
    }
    const std::vector<int> nums{3, 34, 4, 12, 5, 2};
    std::cout << "subset of {3,34,4,12,5,2} summing to 9: "
              << (subsetSum(nums, 0, 9) ? "yes" : "no") << ", to 30: "
              << (subsetSum(nums, 0, 30) ? "yes" : "no") << "\n";

    std::unordered_map<int, long long> memo;
    std::cout << "fib(30) naive = " << fibNaive(30) << ", memo = " << fibMemo(30, memo)
              << ", fib(80) memo = " << fibMemo(80, memo)
              << ", bottom-up = " << fibBottomUp(80) << "\n";

    std::map<std::pair<int, size_t>, long long> wmemo;
    const std::vector<int> coins{1, 2, 5};
    std::cout << "ways to make 100 with {1,2,5}: " << ways(100, 0, coins, wmemo)
              << " (expected 541)\n";
    return 0;
}
