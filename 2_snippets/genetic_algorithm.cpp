// genetic_algorithm.cpp - genetic algorithm on permutations (TSP demo, 15 cities).
// Build: g++ -std=c++17 -Wall -Wextra -O2 genetic_algorithm.cpp -o genetic_algorithm
//
// GA loop (one generation):
//   1. evaluate cost (fitness) of every individual
//   2. elitism: copy the best few unchanged into the next generation
//   3. fill the rest: pick 2 parents by TOURNAMENT selection, CROSSOVER them (OX for
//      permutations), MUTATE the child with small probability, evaluate it
//   4. replace the population, repeat
// Here lower cost = better (tour length). For "maximise", flip the comparisons.
//
// ADAPT: Individual (the genome), cost(), randomIndividual(), crossover(), mutate().
// The loop in evolve() does not care what the genome is.
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

struct City
{
    double x, y;
};

// ---------------------------------------------------------------------------
// Problem definition (ADAPT)
// ---------------------------------------------------------------------------
struct Individual
{
    std::vector<int> genes;    // a permutation of 0..n-1 = visiting order
    double cost = 0.0;         // tour length (lower is better)
};

double tourLength(const std::vector<int> &tour, const std::vector<City> &cities)
{
    double total = 0.0;
    for(size_t i = 0; i < tour.size(); ++i)
    {
        const City &a = cities[static_cast<size_t>(tour[i])];
        const City &b = cities[static_cast<size_t>(tour[(i + 1) % tour.size()])];
        total += std::hypot(a.x - b.x, a.y - b.y);
    }
    return total;
}

Individual randomIndividual(size_t n, std::mt19937 &rng)
{
    Individual ind;
    ind.genes.resize(n);
    std::iota(ind.genes.begin(), ind.genes.end(), 0);   // 0,1,2,...,n-1
    std::shuffle(ind.genes.begin(), ind.genes.end(), rng);
    return ind;
}

// Order crossover (OX): copy a slice of parent 1, fill the rest in the ORDER in which
// the missing cities appear in parent 2 (starting after the slice, wrapping around).
// Always yields a valid permutation.
std::vector<int> orderCrossover(const std::vector<int> &p1, const std::vector<int> &p2,
                                std::mt19937 &rng)
{
    const size_t n = p1.size();
    std::uniform_int_distribution<size_t> pick(0, n - 1);
    size_t a = pick(rng), b = pick(rng);
    if(a > b)
        std::swap(a, b);

    std::vector<int> child(n, -1);
    std::vector<char> used(n, 0);
    for(size_t i = a; i <= b; ++i)
    {
        child[i] = p1[i];
        used[static_cast<size_t>(p1[i])] = 1;
    }
    size_t pos = (b + 1) % n;
    for(size_t k = 0; k < n; ++k)
    {
        const int city = p2[(b + 1 + k) % n];
        if(used[static_cast<size_t>(city)])
            continue;
        child[pos] = city;
        used[static_cast<size_t>(city)] = 1;
        pos = (pos + 1) % n;
    }
    return child;
}

// Mutation 1: swap two random positions.
void swapMutation(std::vector<int> &g, std::mt19937 &rng)
{
    std::uniform_int_distribution<size_t> pick(0, g.size() - 1);
    std::swap(g[pick(rng)], g[pick(rng)]);
}

// Mutation 2: reverse a random slice (like a 2-opt move, usually better for TSP).
void inversionMutation(std::vector<int> &g, std::mt19937 &rng)
{
    std::uniform_int_distribution<size_t> pick(0, g.size() - 1);
    size_t a = pick(rng), b = pick(rng);
    if(a > b)
        std::swap(a, b);
    std::reverse(g.begin() + static_cast<std::ptrdiff_t>(a),
                 g.begin() + static_cast<std::ptrdiff_t>(b) + 1);
}

// ---------------------------------------------------------------------------
// Generic GA machinery
// ---------------------------------------------------------------------------
struct Params
{
    size_t populationSize = 150;
    size_t generations = 300;
    size_t elite = 2;              // best individuals copied unchanged
    size_t tournamentSize = 4;     // bigger = more selection pressure
    double crossoverRate = 0.9;
    double mutationRate = 0.25;
};

// Tournament selection: draw k random individuals, return the best one.
const Individual &tournament(const std::vector<Individual> &pop, size_t k, std::mt19937 &rng)
{
    std::uniform_int_distribution<size_t> pick(0, pop.size() - 1);
    const Individual *best = &pop[pick(rng)];
    for(size_t i = 1; i < k; ++i)
    {
        const Individual *cand = &pop[pick(rng)];
        if(cand->cost < best->cost)
            best = cand;
    }
    return *best;
}

bool isPermutation(const std::vector<int> &g)
{
    std::vector<int> sorted(g);
    std::sort(sorted.begin(), sorted.end());
    for(size_t i = 0; i < sorted.size(); ++i)
        if(sorted[i] != static_cast<int>(i))
            return false;
    return true;
}

Individual evolve(const std::vector<City> &cities, const Params &prm, std::mt19937 &rng,
                  bool verbose)
{
    const size_t n = cities.size();
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    auto byCost = [](const Individual &a, const Individual &b) { return a.cost < b.cost; };

    // initial population
    std::vector<Individual> pop;
    for(size_t i = 0; i < prm.populationSize; ++i)
    {
        pop.push_back(randomIndividual(n, rng));
        pop.back().cost = tourLength(pop.back().genes, cities);    // ADAPT: cost()
    }

    for(size_t gen = 0; gen <= prm.generations; ++gen)
    {
        std::sort(pop.begin(), pop.end(), byCost);       // best first
        if(verbose && gen % 50 == 0)
            std::cout << "gen " << gen << "  best " << pop.front().cost << "\n";
        if(gen == prm.generations)
            break;

        std::vector<Individual> next(pop.begin(), pop.begin() + static_cast<std::ptrdiff_t>(prm.elite));
        while(next.size() < prm.populationSize)
        {
            const Individual &p1 = tournament(pop, prm.tournamentSize, rng);
            const Individual &p2 = tournament(pop, prm.tournamentSize, rng);
            Individual child;
            child.genes = (unit(rng) < prm.crossoverRate)
                              ? orderCrossover(p1.genes, p2.genes, rng)   // ADAPT: crossover
                              : p1.genes;
            if(unit(rng) < prm.mutationRate)
            {
                if(unit(rng) < 0.5)
                    swapMutation(child.genes, rng);                       // ADAPT: mutation
                else
                    inversionMutation(child.genes, rng);
            }
            child.cost = tourLength(child.genes, cities);
            next.push_back(child);
        }
        pop.swap(next);
    }
    return pop.front();
}

int main()
{
    std::mt19937 rng(12345);   // fixed seed -> reproducible run
    std::uniform_real_distribution<double> coord(0.0, 100.0);

    std::vector<City> cities;
    for(int i = 0; i < 15; ++i)
    {
        City c;
        c.x = coord(rng);
        c.y = coord(rng);
        cities.push_back(c);
    }

    // Baseline: nearest-neighbour greedy tour from city 0
    std::vector<int> greedy{0};
    std::vector<char> seen(cities.size(), 0);
    seen[0] = 1;
    while(greedy.size() < cities.size())
    {
        const City &last = cities[static_cast<size_t>(greedy.back())];
        int bestCity = -1;
        double bestD = 1e18;
        for(size_t c = 0; c < cities.size(); ++c)
        {
            if(seen[c])
                continue;
            const double d = std::hypot(last.x - cities[c].x, last.y - cities[c].y);
            if(d < bestD)
            {
                bestD = d;
                bestCity = static_cast<int>(c);
            }
        }
        seen[static_cast<size_t>(bestCity)] = 1;
        greedy.push_back(bestCity);
    }
    std::cout << "nearest-neighbour baseline: " << tourLength(greedy, cities) << "\n";

    Params prm;
    const Individual best = evolve(cities, prm, rng, true);
    std::cout << "GA best length: " << best.cost << "\n";
    std::cout << "tour:";
    for(int c : best.genes)
        std::cout << ' ' << c;
    std::cout << "\nvalid permutation: " << (isPermutation(best.genes) ? "yes" : "NO") << "\n";
    return 0;
}
