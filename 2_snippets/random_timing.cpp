// random_timing.cpp - <random> and <chrono> cheat sheet.
// Build: g++ -std=c++17 -Wall -Wextra -O2 random_timing.cpp -o random_timing
//
// Rules of thumb:
//   * create ONE std::mt19937 engine and pass it by reference (never re-seed in a loop)
//   * never use rand() % n (biased, low quality): use a distribution
//   * fixed seed  -> reproducible runs (debugging, GA comparisons)
//   * random_device seed -> different every run
#include <algorithm>
#include <chrono>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

// Pick a random element of a non-empty vector (returns a reference).
// ADAPT: the container type.
template<class T>
const T &pickRandom(const std::vector<T> &v, std::mt19937 &rng)
{
    std::uniform_int_distribution<size_t> d(0, v.size() - 1);   // bounds are INCLUSIVE
    return v[d(rng)];
}

// Time any callable, returns elapsed milliseconds as double.
template<class F>
double timeMs(F &&f)
{
    const auto t0 = std::chrono::steady_clock::now();
    f();
    const auto t1 = std::chrono::steady_clock::now();
    return std::chrono::duration<double, std::milli>(t1 - t0).count();
}

long long heavySum(int n)
{
    long long s = 0;
    for(int i = 0; i < n; ++i)
        s += (static_cast<long long>(i) * i) % 7;
    return s;
}

int main()
{
    // --- seeding
    std::mt19937 rng(42);
    std::random_device rd;                      // hardware entropy (deterministic on some
    std::mt19937 rngRandom(rd());               // old MinGW builds: fine for exams)
    (void)rngRandom;
    // Alternative seed from the clock:
    // std::mt19937 rng3(static_cast<unsigned int>(
    //     std::chrono::steady_clock::now().time_since_epoch().count()));

    // --- uniform integers in [lo, hi] (both ends included)
    std::uniform_int_distribution<int> dice(1, 6);
    std::cout << "dice:";
    for(int i = 0; i < 8; ++i)
        std::cout << ' ' << dice(rng);
    std::cout << "\n";

    // --- uniform reals in [lo, hi)
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    std::cout << "reals: " << unit(rng) << ' ' << unit(rng) << "\n";

    // --- coin flip with probability p (e.g. mutation rate)
    std::bernoulli_distribution mutate(0.25);
    int hits = 0;
    for(int i = 0; i < 1000; ++i)
        if(mutate(rng))
            ++hits;
    std::cout << "bernoulli(0.25) hits out of 1000: " << hits << "\n";

    // --- gaussian noise
    std::normal_distribution<double> gauss(0.0, 1.0);   // mean, stddev
    std::cout << "gauss: " << gauss(rng) << "\n";

    // --- weighted choice (roulette wheel): index i chosen with prob weights[i]/sum
    std::discrete_distribution<int> roulette({1.0, 2.0, 7.0});
    int counts[3] = {0, 0, 0};
    for(int i = 0; i < 1000; ++i)
        ++counts[roulette(rng)];
    std::cout << "roulette counts (expect ~100/200/700): " << counts[0] << ' ' << counts[1]
              << ' ' << counts[2] << "\n";

    // --- shuffle a vector (never use random_shuffle: removed in C++17)
    std::vector<int> v(10);
    std::iota(v.begin(), v.end(), 0);
    std::shuffle(v.begin(), v.end(), rng);
    std::cout << "shuffled:";
    for(int x : v)
        std::cout << ' ' << x;
    std::cout << "\n";

    // --- random element
    std::vector<std::string> names{"red", "green", "blue"};
    std::cout << "random pick: " << pickRandom(names, rng) << "\n";

    // --- random sample without replacement: shuffle then take first k
    std::shuffle(v.begin(), v.end(), rng);
    std::cout << "sample of 3:";
    for(size_t i = 0; i < 3; ++i)
        std::cout << ' ' << v[i];
    std::cout << "\n";

    // --- timing
    long long result = 0;
    const double ms = timeMs([&result]() { result = heavySum(50000000); });
    std::cout << "heavySum = " << result << " computed in " << ms << " ms\n";

    // Direct chrono (when a lambda is awkward):
    const auto start = std::chrono::steady_clock::now();
    result += heavySum(1000);
    const auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
                             std::chrono::steady_clock::now() - start).count();
    std::cout << "small job: " << elapsed << " us (result " << result << ")\n";
    return 0;
}
