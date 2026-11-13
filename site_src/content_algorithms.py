"""Hand-written content for the Algorithms page and the container-complexity card.
Kept separate from the generator so it is easy to edit."""

DECISION = [
    # (question, answer, algorithm id, why)
    ("Fill a grid / assign values under constraints (sudoku, N-queens, KenKen)?",
     "Backtracking", "backtracking",
     "set a value -> recurse -> cancel. Pick the most constrained cell first."),
    ("Shortest sequence of moves to a goal, with a distance estimate (maze, 15-puzzle)?",
     "A*", "astar",
     "Needs neighboors(), distToPrevious(), h(goal). h must never overestimate."),
    ("Shortest path where every move costs 1 and no heuristic is given?",
     "BFS", "bfs",
     "Queue + visited. First time you reach the goal = shortest."),
    ("Explore everything / count regions / reachability?",
     "DFS / flood fill", "bfs",
     "Recursive or with a stack. Mark visited before recursing."),
    ("Two players taking turns (Connect Four, Nim, tic-tac-toe)?",
     "Minimax + alpha-beta", "minimax",
     "play -> recurse -> undo. Score from the side to move (negamax)."),
    ("Optimise an ordering / parameters with no exact method (TSP)?",
     "Genetic algorithm", "ga",
     "Fitness, selection, crossover that keeps a valid permutation, mutation."),
    ("Same sub-problem computed again and again (counting ways, Fibonacci)?",
     "Recursion + memo", "recursion",
     "Cache results in a map/vector keyed by the arguments."),
]

ALGOS = [
    {
        "id": "backtracking", "name": "Backtracking", "snippet": "backtracking",
        "exam": "Sudoku (past exam)",
        "pseudo": """solve():
  if everything assigned: return true
  x = most constrained open variable      // fewest candidates
  for v in candidates(x):                  // iterate over a COPY
      set(x, v)                            // + prune v from neighbours
      if solve(): return true
      cancel(x)                            // undo EXACTLY what set did
  return false                             // all candidates failed""",
        "implement": ["set / cancel (and prune / restore with a counter)",
                      "is-complete check", "comparator for min_element (best next cell)"],
        "bugs": ["return false INSIDE the loop (only first candidate tried)",
                 "cancel() not restoring what set() pruned",
                 "comparator letting already-filled cells win"],
        "cost": "Exponential worst case; the heuristic is what makes it fast.",
    },
    {
        "id": "astar", "name": "A* search", "snippet": "astar",
        "exam": "Maze (past exam)",
        "pseudo": """open = {start};  g[start] = 0
while open not empty:
    cur = node in open with smallest f = g + h(cur, goal)
    if cur == goal: return path (follow parent)
    move cur from open to closed
    for nb in cur.neighboors():
        if nb in closed: continue
        ng = g[cur] + nb.distToPrevious()
        if nb not in open or ng < g[nb]:
            g[nb] = ng;  parent[nb] = cur;  put nb in open
return no path""",
        "implement": ["neighboors(): only valid, free positions",
                      "distToPrevious() when moves can be longer than 1",
                      "h(goal): Manhattan on grids (never overestimate)",
                      "operator== comparing the state"],
        "bugs": ["neighbours going through walls / out of the grid",
                 "h overestimating -> path not shortest",
                 "operator== comparing the wrong fields"],
        "cost": "With a good h, explores far fewer nodes than BFS.",
    },
    {
        "id": "bfs", "name": "BFS / DFS", "snippet": "bfs_dfs",
        "exam": "Building block (maze, regions)",
        "pseudo": """BFS(start):                              DFS(u):
  queue = {start}; visited = {start}        visited.insert(u)
  while queue not empty:                    for v in neighbours(u):
      u = queue.front(); queue.pop()            if v not visited:
      for v in neighbours(u):                       DFS(v)
          if v not visited:
              visited.insert(v)   // mark when PUSHING
              parent[v] = u
              queue.push(v)""",
        "implement": ["neighbours on a grid: 4 directions, bounds check",
                      "visited as vector<vector<bool>> or set"],
        "bugs": ["marking visited when popping (duplicates in the queue)",
                 "row/column swapped (x = column, y = row)"],
        "cost": "O(V + E). BFS = shortest path when all moves cost 1.",
    },
    {
        "id": "minimax", "name": "Minimax + alpha-beta", "snippet": "minimax_alphabeta",
        "exam": "Likely: Connect Four / Nim",
        "pseudo": """negamax(state, depth, alpha, beta):
    if depth == 0 or state.isTerminal():
        return evaluate(state)            // from the side to move
    best = -INF
    for m in state.validMoves():
        state.play(m)
        score = -negamax(state, depth-1, -beta, -alpha)
        state.undo(m)
        best  = max(best, score)
        alpha = max(alpha, score)
        if alpha >= beta: break           // prune
    return best""",
        "implement": ["validMoves / play / undo (like set / cancel)",
                      "isTerminal + evaluate (sign = side to move)",
                      "bestMove() looping over root moves"],
        "bugs": ["forgetting undo() after the recursive call",
                 "evaluate from the wrong player's view (sign)",
                 "not negating AND swapping alpha/beta"],
        "cost": "b^d without pruning; about b^(d/2) with good move order.",
    },
    {
        "id": "ga", "name": "Genetic algorithm", "snippet": "genetic_algorithm",
        "exam": "Likely: TSP (open project + live example)",
        "pseudo": """pop = N random permutations
repeat G generations:
    sort pop by fitness;  keep E elites
    while new_pop not full:
        a = tournament(pop);  b = tournament(pop)
        child = orderCrossover(a, b)      // stays a valid permutation
        if rand() < p_mut: mutate(child)  // swap or inversion
        new_pop.push_back(child)
    pop = new_pop
return best individual""",
        "implement": ["fitness (tour length: lower = better)",
                      "selection (tournament of k)",
                      "crossover keeping a permutation (OX)",
                      "mutation (swap / reverse a segment)"],
        "bugs": ["crossover producing duplicates (city visited twice)",
                 "minimising vs maximising mixed up",
                 "no elitism -> best solution lost"],
        "cost": "No optimality guarantee; tune population / generations.",
    },
    {
        "id": "recursion", "name": "Recursion + memo", "snippet": "recursion",
        "exam": "Building block (Hanoi, counting)",
        "pseudo": """f(args):
    if base case: return value
    if args in memo: return memo[args]
    r = combine( f(smaller args) ... )
    memo[args] = r
    return r""",
        "implement": ["base case first", "memo keyed by the arguments"],
        "bugs": ["missing base case (stack overflow / segfault)",
                 "memo key missing an argument"],
        "cost": "Memo turns exponential into (number of distinct args) x work.",
    },
]

PATTERNS = [
    ("What his exams look like",
     ["A puzzle or game + one classic algorithm, given as pseudocode in the PDF.",
      "Most classes are provided: you fill in a few methods marked TODO.",
      "Grading = it compiles, then each TODO works, in the subject's order."]),
    ("C++ skills they test",
     ["Classes, member vs accessor (digit_ vs digit()), static functions.",
      "Pointers to other objects (neighbours) and -> .",
      "STL: vector, array, min_element with a comparator, find / erase.",
      "Inheriting from a given class (Position : ecn::Point), operator==.",
      "Reading existing code and reusing it (templates like ecn::Astar)."]),
]

# container complexity: (container, access, push_back/insert end, insert middle/any, find, erase, note)
CONTAINERS = [
    ("vector", "1", "1*", "n", "n", "n", "default choice; contiguous"),
    ("array", "1", "-", "-", "n", "-", "fixed size, stack"),
    ("deque", "1", "1", "n", "n", "n", "push/pop both ends"),
    ("list", "n", "1", "1", "n", "1", "only with an iterator in hand"),
    ("set / map", "log", "log", "log", "log", "log", "sorted, unique keys"),
    ("unordered_set / map", "1", "1", "1", "1", "1", "average; needs hash"),
    ("priority_queue", "top 1", "log", "-", "-", "pop log", "max-heap by default"),
    ("queue / stack", "front 1", "1", "-", "-", "pop 1", "adapters"),
]
