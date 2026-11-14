#include <a_star.h>
#include <maze.h>

using namespace std;
using namespace ecn;

// a node is a x-y position, we move from 1 each time
class Position : public Point
{
public:
    int distance = 1;

    // constructor from coordinates
    Position(int _x, int _y) : Point(_x, _y) {}

    //Constructor with dist to previous
    Position(int _x, int _y, int _distance) : Point(_x, _y)
    {
        distance = _distance;
    }

    // constructor from base ecn::Point
    Position(ecn::Point p) : Point(p.x, p.y) {}

    // goal cell, computed once (maze.end() scans the image and prints): stop on it while sliding
    static bool is_goal(int cx, int cy)
    {
        static const Point g = maze.end();
        return cx == g.x && cy == g.y;
    }

    int distToPrevious() const
    {
        // in cell-based motion, the distance to the previous node is always 1
        return distance;
    }

    std::vector<Position> neighboors() const
    {
        // this method should return  all positions reachable from this one
        std::vector<Position> generated;

        // TODO add free reachable positions from this point
        if (maze.isFree(x-1, y))
        {
            generated.push_back(search(x, y, 1));
        }
        if (maze.isFree(x+1, y))
        {
            generated.push_back(search(x, y, 3));
        }
        if (maze.isFree(x, y-1))
        {
            generated.push_back(search(x, y, 2));
        }
        if (maze.isFree(x, y+1))
        {
            generated.push_back(search(x, y, 4));
        }

        return generated;
    }
    bool is_corridor(int x, int y) const
    {
        if(!maze.isFree(x, y+1) && !maze.isFree(x, y-1) && maze.isFree(x+1, y) && maze.isFree(x-1, y)) return true;
        if(maze.isFree(x, y+1) && maze.isFree(x, y-1) && !maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return true;
        return false;
    }
    int which_corner(int x, int y) const
    {
        if(!maze.isFree(x, y+1) && maze.isFree(x, y-1) && !maze.isFree(x+1, y) && maze.isFree(x-1, y)) return 1; //wall down and right
        if(maze.isFree(x, y+1) && !maze.isFree(x, y-1) && !maze.isFree(x+1, y) && maze.isFree(x-1, y)) return 4; //wall up and right
        if(!maze.isFree(x, y+1) && maze.isFree(x, y-1) && maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return 2; //wall down and left
        if(maze.isFree(x, y+1) && !maze.isFree(x, y-1) && maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return 3; //wall up and left
        return 0;
    }
    bool is_corner(int x, int y) const
    {
        if(!maze.isFree(x, y+1) && maze.isFree(x, y-1) && !maze.isFree(x+1, y) && maze.isFree(x-1, y)) return true; //wall down and right
        if(maze.isFree(x, y+1) && !maze.isFree(x, y-1) && !maze.isFree(x+1, y) && maze.isFree(x-1, y)) return true; //wall up and right
        if(!maze.isFree(x, y+1) && maze.isFree(x, y-1) && maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return true; //wall down and left
        if(maze.isFree(x, y+1) && !maze.isFree(x, y-1) && maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return true; //wall up and left
        return false;
    }
    Position search(int x_s, int y_s, int dir, int distance = 0) const
    {
        int dist = distance;
        if(dir == 1)
        {
            for (int i = 1; ; i++)
            {
                dist++;
                if (is_goal(x_s-i, y_s)) return Position(x_s-i, y_s, dist);
                if(maze.isFree(x_s-i, y_s) && !is_corner(x_s-i, y_s) && !is_corridor(x_s-i, y_s))
                {
                    return Position(x_s-i, y_s, dist);
                }
                else if(is_corner(x_s-i, y_s))
                {
                    int where = which_corner(x_s-i, y_s);
                    if (where == 2)
                    {
                        return search(x_s-i, y_s, 2, dist);
                    }
                    else if (where == 3)
                    {
                        return search(x_s-i, y_s, 4, dist);
                    }
                }

            }

        }
        if(dir == 2) // UP - negative y
        {
            for (int i = 1; ; i++)
            {
                dist++;
                if (is_goal(x_s, y_s-i)) return Position(x_s, y_s-i, dist);
                if(maze.isFree(x_s, y_s-i) && !is_corner(x_s, y_s-i) && !is_corridor(x_s, y_s-i))
                {
                    return(Position(x_s, y_s-i, dist));
                }
                else if(is_corner(x_s, y_s-i))
                {
                    int where = which_corner(x_s, y_s-i);
                    if (where == 3)
                    {
                        return search(x_s, y_s-i, 3, dist);
                    }
                    else if (where == 4)
                    {
                        return search(x_s, y_s-i, 1, dist);
                    }
                }

            }

        }
        if(dir == 3) // RIGHT
        {
            for (int i = 1; ; i++)
            {
                dist++;
                if (is_goal(x_s+i, y_s)) return Position(x_s+i, y_s, dist);
                if(maze.isFree(x_s+i, y_s) && !is_corner(x_s+i, y_s) && !is_corridor(x_s+i, y_s))
                {
                    return(Position(x_s+i, y_s, dist));
                }
                else if(is_corner(x_s+i, y_s))
                {
                    int where = which_corner(x_s+i, y_s);
                    if (where == 1)
                    {
                        return search(x_s+i, y_s, 2, dist);
                    }
                    else if (where == 4)
                    {
                        return search(x_s+i, y_s, 4, dist);
                    }
                }

            }

        }
        if(dir == 4) // DOWN
        {
            for (int i = 1; ; i++)
            {
                dist++;
                if (is_goal(x_s, y_s+i)) return Position(x_s, y_s+i, dist);
                if(maze.isFree(x_s, y_s+i) && !is_corner(x_s, y_s+i) && !is_corridor(x_s, y_s+i))
                {
                    return (Position(x_s, y_s+i, dist));
                }
                else if(is_corner(x_s, y_s+i))
                {
                    int where = which_corner(x_s, y_s+i);
                    if (where == 1)
                    {
                        return search(x_s, y_s+i, 1, dist);
                    }
                    else if (where == 2)
                    {
                        return search(x_s, y_s+i, 3, dist);
                    }
                }

            }

        }

        return Position(x_s, y_s, dist);   // not reached: every walk ends in a return above
    }

    // corridor paths are not straight lines: walk the corridor again and draw the walk that ends on next
    void print(const Point &next) const override
    {
        const int DX[4] = {1, -1, 0, 0}, DY[4] = {0, 0, 1, -1};
        const size_t max_len = (size_t)maze.width() * maze.height();
        for (int d = 0; d < 4; d++)
        {
            int dx = DX[d], dy = DY[d];
            int cx = x + dx, cy = y + dy;
            if (!maze.isFree(cx, cy)) continue;
            std::vector<Point> cells{Point(x, y)};
            while (cells.size() <= max_len)
            {
                cells.push_back(Point(cx, cy));
                if (cx == next.x && cy == next.y)
                {
                    for (const Point &c : cells) maze.passThrough(c.x, c.y);
                    return;
                }
                int exits = 0, ndx = 0, ndy = 0;          // ways out, not counting where we came from
                for (int k = 0; k < 4; k++)
                {
                    if (DX[k] == -dx && DY[k] == -dy) continue;
                    if (maze.isFree(cx + DX[k], cy + DY[k])) { exits++; ndx = DX[k]; ndy = DY[k]; }
                }
                if (exits != 1) break;                    // dead end or intersection: wrong corridor
                dx = ndx; dy = ndy; cx += dx; cy += dy;
            }
        }
    }
};



int main( int argc, char **argv )
{
    // load file
    // let Point know about this maze
    Position::maze.load(argc, argv);

    // initial and goal positions as Position's
    Position start = Position::maze.start(),
             goal = Position::maze.end();

    // call A* algorithm
    ecn::Astar(start, goal);

    // save final image
    Position::maze.saveSolution("corridor");
    cv::waitKey(0);

}
