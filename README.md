# Post-Apocalyptic C++

Offline C++ kit for the **ARPRO** exam (Advanced and Robot Programming, Centrale Nantes, CORO-IMARO). The lab PCs have no internet but any drive is allowed. This is what I put on mine: cheat-sheets, compiling algorithm templates, my practice mistakes and a solved past exam, all searchable from one page.

**Online version:** https://www.leongorecki.eu/Post-Apo-C-plus-plus/START_HERE.html (same page; links to course files point to their public sources).

## Put it on a drive

```bash
git clone https://github.com/leo-01000111/Post-Apo-C-plus-plus.git
cd Post-Apo-C-plus-plus
bash tools/fetch_extras.sh      # course repo, exam subjects, offline cppreference (needs internet, once)
```

Copy the `Post-Apo-C-plus-plus` folder to the root of a USB drive (FAT32 or exFAT, no encryption). The course **slides** are not public: download them from Hippocampus, put the PDFs in `4_course/slides/` and rerun `fetch_extras.sh` to make them searchable.

## On the exam PC (about 10 seconds)

1. Plug in the drive and open it in the file manager (Dolphin).
2. Go into `Post-Apo-C-plus-plus` and press **Shift+F4** ("Open Terminal Here").
3. Run `bash tools/setup.sh`. It copies the kit to `~/Post-Apo-C-plus-plus`, unpacks the portable Firefox there (no admin rights needed), starts the search server and opens the kit and the search page.
4. Closed Firefox by accident? Click **Post-Apo C++** in the app menu or on the desktop (setup creates it), or run `bash ~/Post-Apo-C-plus-plus/tools/open.sh`. It restarts the search if needed and reopens both pages.

Run scripts as `bash script.sh`, not `./script.sh` (drives are often mounted without execute rights). Keep the drive plugged in: the C++ docs are read from it.

## What's inside

| Path | What |
|---|---|
| `START_HERE.html` | Self-contained page: 11 sections incl. a syntax reference of 150 std functions, typo-tolerant Ctrl+K search, copy buttons, exam timer, routine checklist. Works offline and online. |
| `1_cheatsheet/` | Page source: my mistakes, C++17 cheat-sheet, STL quick reference, compiler-error decoder, exam routine (Markdown). |
| `2_snippets/` | Standalone C++17 files that compile warning-free: backtracking, A* (with the course's `ecn::Astar`), BFS/DFS, minimax with alpha-beta, genetic algorithm, containers, random/timing, recursion, CMake template. Lines to change are marked `ADAPT:`. |
| `3_solved_exams/` | My solution to the sudoku exam. |
| `tools/` | `setup.sh` (exam PC), `find.sh` (grep everything), `build.sh` (CMake, `Sanitize` mode), `test_snippets.sh`, `fetch_extras.sh`. |
| `site_src/` | Generator for `START_HERE.html`; `functions.py` is the syntax reference, `python site_src/test_functions.py` compiles all its examples. |
| `tools/search/` | Offline search engine: SQLite full-text index (BM25) over cppreference, Stack Overflow, the function reference and the kit, with typo correction; local search page on http://127.0.0.1:8090 (Python standard library only). |
| `4_course/`, `5_repo/`, `6_reference/` | Not in the repo (third-party). Created by `fetch_extras.sh`. |
| `7_stackoverflow/`, `8_search/`, `9_browser/` | Not in the repo. Top 5,000 Stack Overflow [c++] Q&As (CC BY-SA, see `7_stackoverflow/ATTRIBUTION.md`), the built index, portable Firefox ESR. Created by `fetch_extras.sh`. |

## Terminal tools

```bash
bash tools/search.sh "erase while iterating" # ranked search: cppreference, Stack Overflow, functions, kit
bash tools/search.sh                        # same, as a page in the browser
bash tools/find.sh priority_queue          # grep cheat-sheets, snippets, exams, slide text, course repo
bash tools/find.sh -C 3 "erase.*remove"     # regex, with context
bash tools/build.sh path/to/project Sanitize   # crash -> exact line (AddressSanitizer + UBSan)
bash tools/test_snippets.sh                 # compile and run every snippet
```

## Rebuild the page

Edit the Markdown in `1_cheatsheet/`, the snippets, or `site_src/content_algorithms.py`, then:

```bash
pip install markdown pygments
python site_src/build_site.py
```

## Credits

- Design: Holding Point, the design system of [leongorecki.eu](https://www.leongorecki.eu/). Fonts Archivo and Martian Mono (SIL Open Font License), embedded in the page.
- Course material (not included): Olivier Kermorgant, [ecn_arpro](https://github.com/oKermorgant/ecn_arpro).
- Offline reference (not included): [cppreference.com](https://en.cppreference.com/) via [cppreference-doc](https://github.com/PeterFeicht/cppreference-doc), CC-BY-SA.

Made by [Leon Górecki](https://www.leongorecki.eu/).
