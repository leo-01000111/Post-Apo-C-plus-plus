// minimax_alphabeta.cpp - negamax + alpha-beta (and plain minimax) on a generic game
// interface. Demos: Nim sticks and Connect Four 6x7.
// Build: g++ -std=c++17 -Wall -Wextra -O2 minimax_alphabeta.cpp -o minimax_alphabeta
//
// Game interface (what YOUR game class must provide; ADAPT everything below it):
//     using Move = int;                          // any copyable type
//     std::vector<Move> validMoves() const;      // legal moves for the player to move
//     void play(const Move &m);                  // apply move, switch player
//     void undo(const Move &m);                  // exact inverse of play(m), switch back
//     bool isTerminal() const;                   // game over (win/loss/draw)?
//     int  evaluate() const;                     // score FROM THE POINT OF VIEW OF THE
//                                                // PLAYER TO MOVE: >0 good for him.
//                                                // Lost position (previous mover just won)
//                                                // must return -WIN. Draw -> 0.
//
// Negamax trick: score(player) = -score(opponent), so ONE function replaces the
// separate max and min functions of textbook minimax:
//     value = -negamax(child, depth-1, -beta, -alpha)
// alpha = best score the player to move is already sure of,
// beta  = best score the opponent would allow. If alpha >= beta -> prune (break).
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

const int WIN = 100000;   // score of a won position (heuristics must stay far below)

template<class Move>
struct SearchResult
{
    Move move{};
    int score = 0;
    long nodes = 0;
};

// ---------------------------------------------------------------------------
// Plain negamax WITHOUT pruning (for comparison / simplest correct version).
// ---------------------------------------------------------------------------
template<class G>
int negamaxPlain(G &g, int depth, long &nodes)
{
    ++nodes;
    if(g.isTerminal() || depth == 0)
    {
        int s = g.evaluate();
        if(s >= WIN) s += depth;            // prefer quicker wins...
        else if(s <= -WIN) s -= depth;      // ...and slower losses
        return s;
    }
    int best = -2 * WIN;
    for(const auto &m : g.validMoves())
    {
        g.play(m);
        best = std::max(best, -negamaxPlain(g, depth - 1, nodes));
        g.undo(m);
    }
    return best;
}

// ---------------------------------------------------------------------------
// Negamax with alpha-beta pruning and a depth limit. Call with
// alpha = -2*WIN, beta = 2*WIN at the root.
// ---------------------------------------------------------------------------
template<class G>
int negamax(G &g, int depth, int alpha, int beta, long &nodes)
{
    ++nodes;
    if(g.isTerminal() || depth == 0)
    {
        int s = g.evaluate();               // ADAPT: heuristic at depth limit
        if(s >= WIN) s += depth;
        else if(s <= -WIN) s -= depth;
        return s;
    }
    int best = -2 * WIN;
    for(const auto &m : g.validMoves())     // ADAPT: move ORDERING matters a lot
    {
        g.play(m);
        const int v = -negamax(g, depth - 1, -beta, -alpha, nodes);
        g.undo(m);
        if(v > best)
            best = v;
        if(best > alpha)
            alpha = best;
        if(alpha >= beta)
            break;                          // cut-off: opponent will never allow this line
    }
    return best;
}

// Root: tries every move and returns the best one (with score and node count).
template<class G>
SearchResult<typename G::Move> bestMove(G &g, int depth, bool prune = true)
{
    SearchResult<typename G::Move> res;
    int alpha = -2 * WIN;
    const int beta = 2 * WIN;
    int best = -4 * WIN;
    for(const auto &m : g.validMoves())
    {
        g.play(m);
        const int v = prune ? -negamax(g, depth - 1, -beta, -alpha, res.nodes)
                            : -negamaxPlain(g, depth - 1, res.nodes);
        g.undo(m);
        if(v > best)
        {
            best = v;
            res.move = m;
        }
        if(best > alpha)
            alpha = best;
    }
    res.score = best;
    return res;
}

// Textbook version with an explicit maximizing flag, evaluate() from a FIXED player's
// point of view (not the mover's). Kept only as a reference of the non-negamax form.
//   int minimax(G &g, int depth, bool maximizing) {
//       if (g.isTerminal() || depth == 0) return g.evaluateFor(maxPlayer);
//       int best = maximizing ? -INF : +INF;
//       for (m : g.validMoves()) {
//           g.play(m);
//           int v = minimax(g, depth - 1, !maximizing);
//           g.undo(m);
//           best = maximizing ? std::max(best, v) : std::min(best, v);
//       }
//       return best;
//   }

// ---------------------------------------------------------------------------
// Game 1: Nim with sticks. Take 1..3 sticks, whoever takes the LAST stick wins.
// (Variant "last stick loses": change evaluate() to +WIN when sticks == 0, since then
//  the player to move has WON because the opponent took the last one.)
// ---------------------------------------------------------------------------
class Nim
{
public:
    using Move = int;
    explicit Nim(int sticks) : sticks_(sticks) {}

    std::vector<int> validMoves() const
    {
        std::vector<int> m;
        for(int k = 1; k <= 3 && k <= sticks_; ++k)   // ADAPT: max take
            m.push_back(k);
        return m;
    }
    void play(const int &k) { sticks_ -= k; }
    void undo(const int &k) { sticks_ += k; }
    bool isTerminal() const { return sticks_ == 0; }
    int evaluate() const { return sticks_ == 0 ? -WIN : 0; }  // mover facing 0 sticks lost
    int sticks() const { return sticks_; }

private:
    int sticks_;
};

// ---------------------------------------------------------------------------
// Game 2: Connect Four, 6 rows x 7 columns. Players are +1 (first) and -1 (second).
// Move = column index 0..6.
// ---------------------------------------------------------------------------
class Connect4
{
public:
    using Move = int;
    static constexpr int ROWS = 6;
    static constexpr int COLS = 7;

    Connect4() : turn_(1)
    {
        for(int r = 0; r < ROWS; ++r)
            for(int c = 0; c < COLS; ++c)
                b_[r][c] = 0;
        for(int c = 0; c < COLS; ++c)
            h_[c] = 0;
    }

    // Centre columns first: good ordering = many more cut-offs.
    std::vector<int> validMoves() const
    {
        static const int order[COLS] = {3, 2, 4, 1, 5, 0, 6};
        std::vector<int> m;
        for(int k = 0; k < COLS; ++k)
            if(h_[order[k]] < ROWS)
                m.push_back(order[k]);
        return m;
    }

    void play(const int &c)
    {
        b_[h_[c]][c] = turn_;
        ++h_[c];
        hist_.push_back(c);
        turn_ = -turn_;
    }

    void undo(const int &c)
    {
        --h_[c];
        b_[h_[c]][c] = 0;
        hist_.pop_back();
        turn_ = -turn_;
    }

    // Did the disc that was just played complete four in a row?
    bool lastMoveWon() const
    {
        if(hist_.empty())
            return false;
        const int c = hist_.back();
        const int r = h_[c] - 1;
        const int p = b_[r][c];
        static const int dir[4][2] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};
        for(int d = 0; d < 4; ++d)
        {
            int n = 1;
            for(int sign = -1; sign <= 1; sign += 2)
                for(int k = 1; k < 4; ++k)
                {
                    const int rr = r + sign * dir[d][0] * k;
                    const int cc = c + sign * dir[d][1] * k;
                    if(rr < 0 || rr >= ROWS || cc < 0 || cc >= COLS || b_[rr][cc] != p)
                        break;
                    ++n;
                }
            if(n >= 4)
                return true;
        }
        return false;
    }

    bool full() const { return hist_.size() == static_cast<size_t>(ROWS * COLS); }
    bool isTerminal() const { return lastMoveWon() || full(); }

    // Score for the player TO MOVE.
    int evaluate() const
    {
        if(lastMoveWon())
            return -WIN;          // the previous mover just won
        if(full())
            return 0;
        int score = 0;
        // centre column is worth a bit
        for(int r = 0; r < ROWS; ++r)
            score += 3 * b_[r][COLS / 2] * turn_;
        // every window of 4 cells
        static const int dir[4][2] = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};
        for(int r = 0; r < ROWS; ++r)
            for(int c = 0; c < COLS; ++c)
                for(int d = 0; d < 4; ++d)
                {
                    const int er = r + 3 * dir[d][0], ec = c + 3 * dir[d][1];
                    if(er < 0 || er >= ROWS || ec < 0 || ec >= COLS)
                        continue;
                    int mine = 0, theirs = 0;
                    for(int k = 0; k < 4; ++k)
                    {
                        const int v = b_[r + k * dir[d][0]][c + k * dir[d][1]] * turn_;
                        if(v > 0) ++mine;
                        else if(v < 0) ++theirs;
                    }
                    if(mine > 0 && theirs > 0)
                        continue;
                    if(mine == 3) score += 50;
                    else if(mine == 2) score += 10;
                    else if(mine == 1) score += 1;
                    if(theirs == 3) score -= 50;
                    else if(theirs == 2) score -= 10;
                    else if(theirs == 1) score -= 1;
                }
        return score;
    }

    void print() const
    {
        for(int r = ROWS - 1; r >= 0; --r)
        {
            for(int c = 0; c < COLS; ++c)
                std::cout << (b_[r][c] > 0 ? 'X' : (b_[r][c] < 0 ? 'O' : '.')) << ' ';
            std::cout << "\n";
        }
        std::cout << "0 1 2 3 4 5 6\n";
    }

    int turn() const { return turn_; }

private:
    int b_[ROWS][COLS];   // b_[0] = bottom row
    int h_[COLS];         // number of discs in each column
    int turn_;            // +1 or -1: who plays next
    std::vector<int> hist_;
};

int main()
{
    // --- Nim: 21 sticks, the winning move is to leave a multiple of 4 -> take 1
    {
        Nim nim(21);
        const auto r = bestMove(nim, 99);
        std::cout << "Nim 21 sticks: best take = " << r.move << " (score " << r.score
                  << ", alpha-beta nodes " << r.nodes << ")\n";
        Nim nim2(21);
        const auto r2 = bestMove(nim2, 99, false);
        std::cout << "  same without pruning: best take = " << r2.move
                  << ", nodes " << r2.nodes << "\n";
    }

    // --- Connect Four: tactical position, X has 3 in a row on the bottom and must win
    {
        Connect4 g;
        const int opening[] = {3, 3, 4, 4, 5, 5};
        for(int c : opening)
            g.play(c);
        g.print();
        const auto r = bestMove(g, 4);
        std::cout << "X to move, best column = " << r.move << " (score " << r.score
                  << ", nodes " << r.nodes << ")  -> 2 or 6 wins at once\n";
    }

    // --- Connect Four: computer vs computer for a few moves (depth 6)
    {
        Connect4 g;
        long totalNodes = 0;
        for(int move = 0; move < 8 && !g.isTerminal(); ++move)
        {
            const auto r = bestMove(g, 6);
            totalNodes += r.nodes;
            std::cout << (g.turn() > 0 ? "X" : "O") << " plays column " << r.move
                      << " (score " << r.score << ", nodes " << r.nodes << ")\n";
            g.play(r.move);
        }
        g.print();
        std::cout << "total nodes: " << totalNodes << "\n";
    }
    return 0;
}
