# Exam routine

Exam: Mon 16 Nov 2026, 08:00-10:00, lab PCs (Linux). Offline. Thumb drive allowed.

## Exam routine

1. Read the whole subject first.
2. Build the untouched project before changing anything.
3. `git init` + commit after each method that works.
4. Do the TODOs in the subject's order.
5. Never hand in code that doesn't compile: comment out the broken part.

## Time plan (2 h)

| Time | What |
|------|------|
| 0:00 - 0:10 | Read the whole subject PDF + the code skeleton. Build the untouched project. `git init`. Note the TODOs in order. |
| 0:10 - 1:45 | Do the TODOs one by one, in the subject's order. Commit after each one that works. |
| 1:45 - 2:00 | Stop adding features. Clean build from scratch, make sure it compiles, run once, commit. Comment out anything broken. |

Rule: the last 10 minutes are for "it compiles and is committed", not for new code.

## Quick git

```bash
cd <project dir>
git init && git add -A && git commit -qm start     # once, at the start (after the first build works)
git add -A && git commit -qm "step N works"        # after each working method
git log --oneline                                  # check
git stash                                          # park a broken attempt (git stash pop to restore)
git checkout -- file.cpp                           # throw away edits to one file (careful)
```

If git complains about identity:
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

- **Stuck for more than 10 minutes on one TODO: move to the next one.** Leave a `// TODO unfinished` comment, make sure it compiles, come back at the end.
- **The subject PDF contains the algorithm pseudocode: translate it line by line.** Same variable names, same order, same loop structure. Do not "improve" it. Each pseudocode line becomes one C++ line (or a few).
- Read the compiler error from the FIRST one only (later ones are often consequences). See `compiler_errors.md`.
- Check provided helpers before writing your own (e.g. `eraseCandidate`, `print`, `distToPrevious`).
- Read the comments in the provided headers: they state what each method must do.
- Print intermediate values (`std::cout`) rather than guessing; remove noisy prints at the end.
- Re-read `my_mistakes.md` once before starting and once at the 1 h mark.
- Use `find.sh <word>` (greps the whole stick) when you need a snippet: `2_snippets/` has backtracking, A* Node, minimax, GA, CMake.

## Before handing in

- [ ] `rm -rf build && mkdir build && cd build && cmake .. && make` succeeds with no errors.
- [ ] Program runs and gives a plausible result on the given input.
- [ ] Broken/unfinished code is commented out, not left half-written.
- [ ] `git add -A && git commit -qm final`.
- [ ] No debug prints flooding the output; no `waitKey(0)` surprises left unexplained.
