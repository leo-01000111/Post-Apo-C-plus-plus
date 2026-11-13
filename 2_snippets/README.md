# 2_snippets - copy-paste C++17 building blocks

Every `.cpp` is standalone: `g++ -std=c++17 -Wall -Wextra -O2 file.cpp -o file && ./file`.
Search for `ADAPT:` to find what to change. Check all files with `bash ../tools/test_snippets.sh`.

- `backtracking.cpp` - set/cancel recursive search (N-queens demo). Copy: `solveFirst`, `countAll`, generic `backtrack<State,Decision,Value>`, `solveMostConstrained` (min_element heuristic).
- `astar.cpp` - generic A* with the professor's Node interface (`neighboors`, `distToPrevious`, `==`, `h`). Copy: namespace `astar_snip` + `astar` / `astarKeyed`; demo node `Puzzle` (8-puzzle, Manhattan, `solvable`). Bottom: how to use the course's `ecn::Astar` (needs `int h` and `print(next)`).
- `bfs_dfs.cpp` - grid search on `vector<string>`. Copy: `bfs` (shortest path), `bfsDistances`, `dfsRecursive`, `dfsIterativeOrder`, `floodFill`, `countRegions`.
- `minimax_alphabeta.cpp` - game interface (`validMoves/play/undo/isTerminal/evaluate`) + `negamax` alpha-beta, `negamaxPlain`, `bestMove`; demo games `Nim` (sticks) and `Connect4` (6x7).
- `genetic_algorithm.cpp` - GA on permutations (TSP). Copy: `evolve`, `tournament`, `orderCrossover` (OX), `swapMutation`, `inversionMutation`, `tourLength`, `Params`.
- `containers_tricks.cpp` - min-heap `priority_queue` (greater / struct / lambda), `unordered_map` with `PairHash`, `set` of structs with `operator<`, erase-remove, multi-key sort with `std::tie`, `min_element` with comparator.
- `random_timing.cpp` - `mt19937` seeding, uniform int/real, bernoulli, `discrete_distribution`, `shuffle`, `pickRandom`, `timeMs` (chrono).
- `recursion.cpp` - `hanoi`, `permute`, `subsets` / `subsetsMask`, `subsetSum`, memoisation (`fibMemo`, `ways`).
- `CMakeLists_template.txt` - project template: C++17, Release default, `-DSANITIZE=ON`, `-Wall -Wextra`, optional OpenCV / yaml-cpp.
