# Exam routine

Mon 16 Nov 2026, 08:00-10:00, Linux lab PCs, offline, thumb drive allowed.

## Exam routine

1. Read the whole subject first.
2. Build the untouched project before changing anything.
3. `git init` + commit after each method that works.
4. Do the TODOs in the subject's order.
5. Never hand in code that does not compile: comment out the broken part.

## Time plan (2 h)

| Time | What |
|------|------|
| 0:00 - 0:10 | Read the subject PDF and code skeleton. Build the untouched project. `git init`. Note the TODOs in order. |
| 0:10 - 1:45 | Do the TODOs in the subject's order. Commit after each one that works. |
| 1:45 - 2:00 | No new features. Clean build, run once, commit. Comment out anything broken. |

The last 10 minutes are for "it compiles and is committed", not new code.

## Quick git

```bash
cd <project dir>
git init && git add -A && git commit -qm start     # once, after the first build works
git add -A && git commit -qm "step N works"        # after each working method
git log --oneline
git stash                                          # park a broken attempt (git stash pop to restore)
git checkout -- file.cpp                           # throw away edits to one file (careful)
```

Identity error:
```bash
git config user.email "me@x" && git config user.name "me"
```
Do not commit the `build/` folder: `echo build/ > .gitignore` before `git add -A`.

## Clean build

```bash
rm -rf build && mkdir build && cd build && cmake .. && make -j4
# or: cmake -DCMAKE_BUILD_TYPE=Release ..   (much faster backtracking)
# or: cmake -DCMAKE_BUILD_TYPE=Debug ..     (for gdb)
```
New .cpp file added? Re-run `cmake ..` (and check it is in add_executable / the glob).

## Working rules

- Stuck for more than 10 minutes on a TODO: move on. Leave a `// TODO unfinished` comment, keep it compiling, come back at the end.
- The subject PDF has the algorithm pseudocode: translate it line by line, same variable names, order and loop structure. Do not "improve" it.
- Read only the FIRST compiler error (later ones are often consequences). See `compiler_errors.md`.
- Check provided helpers before writing your own (e.g. `eraseCandidate`, `print`, `distToPrevious`).
- The comments in the provided headers state what each method must do.
- Print intermediate values (`std::cout`) instead of guessing; remove noisy prints at the end.
- Re-read `my_mistakes.md` once before starting and once at the 1 h mark.
- `find.sh <word>` greps the whole stick; `2_snippets/` has backtracking, A* Node, minimax, GA, CMake.

## Before handing in

- [ ] `rm -rf build && mkdir build && cd build && cmake .. && make` succeeds with no errors.
- [ ] Program runs and gives a plausible result.
- [ ] Broken/unfinished code is commented out, not left half-written.
- [ ] `git add -A && git commit -qm final`.
- [ ] No debug prints flooding the output; no `waitKey(0)` surprises left unexplained.
