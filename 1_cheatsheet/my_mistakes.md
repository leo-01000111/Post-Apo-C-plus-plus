# My own mistakes (read this first)

- **Members vs accessors.** Inside the class: `digit_`, `candidates_`, `neighboors_`. From another class (e.g. `Grid`): only the public accessors `digit()`, `candidates()`, `neighboors()`. Without the `()`, the name is the function itself, not its value.
- **Accessor returning an array:** `cell.neighboors()[i]`, not `cell.neighboors(i)`.
- **Pointers use `->`:** `neighboors_` holds `Cell*`, so `nb->prune(guess)`.
- **`private` is per class, not per object:** a `Cell` can call `prune` on another `Cell`. `Grid` can't, so it uses the public `eraseCandidate`.
- **`std::vector` has no `.remove()`.** Use `v.erase(it)`, and only when `it != v.end()` (erasing `end()` crashes). Check for a provided helper first (`eraseCandidate` does find + erase safely).
- **Size is `.size()`**, not `.len()` (Python).
- **A 1-D `std::array<Cell, 81>` used as a grid:** `cells[9*row + col]`, not `cells[row][col]`.
- **Loop index vs `.size()`:** use `size_t i` or a range-for, otherwise signed/unsigned warning.
- **`if (in == true)` is just `if (in)`.**
- **Prefer range-for to index loops:**
  ```cpp
  for (auto &cell : cells)                 // & = no copy (Cell can't be copied anyway)
      if (cell.digit() != 0)
          for (auto nb : cell.neighboors())  // nb is a Cell*
              nb->eraseCandidate(cell.digit());
  ```
- **Order matters in undo functions:** in `cancel()`, use `digit_` (restore on the neighbours) *before* resetting it to 0.
- **Backtracking: no `return false` inside the candidate loop.** After `cancel()`, fall through to the next candidate; `return false` goes *after* the loop (all candidates failed). A `return` inside the loop = only the first candidate is ever tried.
- **Program "hangs" after an OpenCV window opens?** It is `cv::waitKey(0)`: click the window and **press a key** in it. (`QSettings::value: Empty key passed` is harmless Qt noise.)
- **Backtracking "stuck" on a hard input?** Usually just exponential: pick the most constrained cell first (fewest candidates) and build in Release (`cmake -DCMAKE_BUILD_TYPE=Release ..`).
- **`vec1 < vec2` compares contents (dictionary order), not lengths.** For "fewer elements", compare `vec1.size() < vec2.size()`.
- **Comparator for `min_element`:** returns `true` if `c1` is *better*. Rule out invalid items first (`if (c1.digit()) return false; if (c2.digit()) return true;`), then compare.
- **Bookkeeping line:** `prune` must increment `pruned_count_[guess]` "in any case", otherwise `restore` breaks.
- **Type vs object (maze exam):** `Maze.isFree(x, y)` does not compile (`expected unqualified-id before '.'`): `Maze` is a class. `Maze().isFree(x, y)` compiles but creates a NEW empty maze, so every cell is a wall and A* finds no path. Use the loaded object: the static member `maze` (`Point::maze`), i.e. `maze.isFree(x, y)`.
