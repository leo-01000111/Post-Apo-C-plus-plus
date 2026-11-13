// bfs_dfs.cpp - BFS shortest path, recursive + iterative DFS, flood fill on a char grid.
// Build: g++ -std=c++17 -Wall -Wextra -O2 bfs_dfs.cpp -o bfs_dfs
//
// Grid convention used here: vector<string>, '#' = wall, ' ' or '.' = free,
// 'S' = start, 'G' = goal. Cell = (row, col).
// ADAPT: isFree() decides what is walkable; DR/DC list the allowed moves
// (4 neighbours here; add the 4 diagonals for 8-connectivity).
#include <algorithm>
#include <iostream>
#include <queue>
#include <stack>
#include <string>
#include <utility>
#include <vector>

using Grid = std::vector<std::string>;
using Cell = std::pair<int, int>;   // (row, col)

const int DR[4] = {-1, 1, 0, 0};
const int DC[4] = {0, 0, -1, 1};

bool inside(const Grid &g, int r, int c)
{
    return r >= 0 && r < static_cast<int>(g.size())
        && c >= 0 && c < static_cast<int>(g[static_cast<size_t>(r)].size());
}

// ADAPT: what can we walk on?
bool isFree(const Grid &g, int r, int c)
{
    return inside(g, r, c) && g[static_cast<size_t>(r)][static_cast<size_t>(c)] != '#';
}

Cell findChar(const Grid &g, char ch)
{
    for(size_t r = 0; r < g.size(); ++r)
        for(size_t c = 0; c < g[r].size(); ++c)
            if(g[r][c] == ch)
                return Cell(static_cast<int>(r), static_cast<int>(c));
    return Cell(-1, -1);
}

// BFS: shortest path (fewest steps) on an unweighted grid.
// Returns the path start..goal, empty if unreachable.
std::vector<Cell> bfs(const Grid &g, Cell start, Cell goal)
{
    const size_t rows = g.size();
    const size_t cols = g.empty() ? 0 : g[0].size();
    // parent[r][c] = cell we came from; (-1,-1) = not visited yet
    std::vector<std::vector<Cell>> parent(rows, std::vector<Cell>(cols, Cell(-1, -1)));
    std::queue<Cell> q;
    q.push(start);
    parent[static_cast<size_t>(start.first)][static_cast<size_t>(start.second)] = start;

    while(!q.empty())
    {
        const Cell cur = q.front();
        q.pop();
        if(cur == goal)
        {
            std::vector<Cell> path;
            for(Cell p = goal; p != start;
                p = parent[static_cast<size_t>(p.first)][static_cast<size_t>(p.second)])
                path.push_back(p);
            path.push_back(start);
            std::reverse(path.begin(), path.end());
            return path;
        }
        for(int k = 0; k < 4; ++k)
        {
            const int nr = cur.first + DR[k], nc = cur.second + DC[k];
            if(!isFree(g, nr, nc))
                continue;
            Cell &par = parent[static_cast<size_t>(nr)][static_cast<size_t>(nc)];
            if(par.first != -1)          // already visited
                continue;
            par = cur;
            q.push(Cell(nr, nc));
        }
    }
    return {};
}

// BFS distance map (-1 = unreachable).
std::vector<std::vector<int>> bfsDistances(const Grid &g, Cell start)
{
    const size_t rows = g.size();
    const size_t cols = g.empty() ? 0 : g[0].size();
    std::vector<std::vector<int>> dist(rows, std::vector<int>(cols, -1));
    std::queue<Cell> q;
    q.push(start);
    dist[static_cast<size_t>(start.first)][static_cast<size_t>(start.second)] = 0;
    while(!q.empty())
    {
        const Cell cur = q.front();
        q.pop();
        const int d = dist[static_cast<size_t>(cur.first)][static_cast<size_t>(cur.second)];
        for(int k = 0; k < 4; ++k)
        {
            const int nr = cur.first + DR[k], nc = cur.second + DC[k];
            if(!isFree(g, nr, nc) ||
               dist[static_cast<size_t>(nr)][static_cast<size_t>(nc)] != -1)
                continue;
            dist[static_cast<size_t>(nr)][static_cast<size_t>(nc)] = d + 1;
            q.push(Cell(nr, nc));
        }
    }
    return dist;
}

// Recursive DFS: finds A path (not the shortest). 'path' is built with push/pop = backtracking.
bool dfsRec(const Grid &g, Cell cur, Cell goal,
            std::vector<std::vector<char>> &seen, std::vector<Cell> &path)
{
    seen[static_cast<size_t>(cur.first)][static_cast<size_t>(cur.second)] = 1;
    path.push_back(cur);
    if(cur == goal)
        return true;
    for(int k = 0; k < 4; ++k)
    {
        const int nr = cur.first + DR[k], nc = cur.second + DC[k];
        if(!isFree(g, nr, nc) || seen[static_cast<size_t>(nr)][static_cast<size_t>(nc)])
            continue;
        if(dfsRec(g, Cell(nr, nc), goal, seen, path))
            return true;
    }
    path.pop_back();     // dead end: undo
    return false;
}

std::vector<Cell> dfsRecursive(const Grid &g, Cell start, Cell goal)
{
    std::vector<std::vector<char>> seen(g.size(), std::vector<char>(g[0].size(), 0));
    std::vector<Cell> path;
    if(!dfsRec(g, start, goal, seen, path))
        path.clear();
    return path;
}

// Iterative DFS with an explicit stack (no recursion depth limit). Returns visit order.
// To rebuild a path, store parent[] exactly like in bfs().
std::vector<Cell> dfsIterativeOrder(const Grid &g, Cell start)
{
    std::vector<std::vector<char>> seen(g.size(), std::vector<char>(g[0].size(), 0));
    std::vector<Cell> order;
    std::stack<Cell> st;
    st.push(start);
    while(!st.empty())
    {
        const Cell cur = st.top();
        st.pop();
        char &s = seen[static_cast<size_t>(cur.first)][static_cast<size_t>(cur.second)];
        if(s)
            continue;
        s = 1;
        order.push_back(cur);
        for(int k = 0; k < 4; ++k)
        {
            const int nr = cur.first + DR[k], nc = cur.second + DC[k];
            if(isFree(g, nr, nc) && !seen[static_cast<size_t>(nr)][static_cast<size_t>(nc)])
                st.push(Cell(nr, nc));
        }
    }
    return order;
}

// Flood fill (modifies the grid): replace the connected region around (r,c) by 'fill'.
// Returns the number of cells changed.
// ADAPT: 'target' is the character being replaced (read from the start cell).
int floodFill(Grid &g, int r, int c, char fill)
{
    if(!inside(g, r, c))
        return 0;
    const char target = g[static_cast<size_t>(r)][static_cast<size_t>(c)];
    if(target == fill)
        return 0;
    int count = 0;
    std::stack<Cell> st;
    st.push(Cell(r, c));
    while(!st.empty())
    {
        const Cell cur = st.top();
        st.pop();
        if(!inside(g, cur.first, cur.second))
            continue;
        char &ch = g[static_cast<size_t>(cur.first)][static_cast<size_t>(cur.second)];
        if(ch != target)
            continue;
        ch = fill;
        ++count;
        for(int k = 0; k < 4; ++k)
            st.push(Cell(cur.first + DR[k], cur.second + DC[k]));
    }
    return count;
}

// Count connected free regions (components) using floodFill on a copy.
int countRegions(Grid g)
{
    int regions = 0;
    // normalise: every non-wall char ('S', 'G', ...) becomes '.', so one region = one colour
    for(std::string &row : g)
        for(char &ch : row)
            if(ch != '#')
                ch = '.';
    for(size_t r = 0; r < g.size(); ++r)
        for(size_t c = 0; c < g[r].size(); ++c)
            if(g[r][c] != '#' && g[r][c] != '~')
            {
                floodFill(g, static_cast<int>(r), static_cast<int>(c), '~');
                ++regions;
            }
    return regions;
}

void printGrid(const Grid &g)
{
    for(const std::string &row : g)
        std::cout << row << "\n";
}

int main()
{
    Grid maze = {
        "S...#.......",
        ".##.#.#####.",
        ".#..#.#...#.",
        ".#.##.#.#.#.",
        ".#....#.#...",
        ".######.###.",
        "........#..G",
    };
    const Cell start = findChar(maze, 'S');
    const Cell goal = findChar(maze, 'G');

    const std::vector<Cell> sp = bfs(maze, start, goal);
    std::cout << "BFS shortest path: " << (sp.empty() ? 0 : sp.size() - 1) << " steps\n";
    Grid shown = maze;
    for(const Cell &c : sp)
        if(shown[static_cast<size_t>(c.first)][static_cast<size_t>(c.second)] == '.')
            shown[static_cast<size_t>(c.first)][static_cast<size_t>(c.second)] = '*';
    printGrid(shown);

    const auto dist = bfsDistances(maze, start);
    std::cout << "distance map says goal is at "
              << dist[static_cast<size_t>(goal.first)][static_cast<size_t>(goal.second)] << "\n";

    const std::vector<Cell> dp = dfsRecursive(maze, start, goal);
    std::cout << "DFS (recursive) found a path of " << (dp.empty() ? 0 : dp.size() - 1)
              << " steps (not necessarily shortest)\n";

    const std::vector<Cell> order = dfsIterativeOrder(maze, start);
    std::cout << "iterative DFS visited " << order.size() << " cells\n";

    std::cout << "free regions before: " << countRegions(maze) << "\n";
    Grid filled = maze;
    const int n = floodFill(filled, 0, 1, 'o');
    std::cout << "flood fill from (0,1) changed " << n << " cells:\n";
    printGrid(filled);

    Grid split = {
        "..#..",
        "..#..",
        "###..",
    };
    std::cout << "regions in the split grid: " << countRegions(split) << "\n";
    return 0;
}
