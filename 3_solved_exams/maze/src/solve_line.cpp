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
            int x_it = x-1;
            while (is_corridor(x_it, y) && !is_goal(x_it, y)) {
                x_it--;
            }
            generated.push_back(Position(x_it, y, abs(x-x_it)));
        }
        if (maze.isFree(x+1, y))
        {
            int x_it = x+1;
            while (is_corridor(x_it, y) && !is_goal(x_it, y)) {
                x_it++;
            }
            generated.push_back(Position(x_it, y, abs(x-x_it)));
        }
        if (maze.isFree(x, y-1))
        {
            int y_it = y-1;
            while (is_corridor(x, y_it) && !is_goal(x, y_it)) {
                y_it--;
            }
            generated.push_back(Position(x, y_it, abs(y-y_it)));
        }
        if (maze.isFree(x, y+1))
        {
            int y_it = y+1;
            while (is_corridor(x, y_it) && !is_goal(x, y_it)) {
                y_it++;
            }
            generated.push_back(Position(x, y_it, abs(y-y_it)));
        }

        return generated;
    }

    bool is_corridor(int x, int y) const
    {
        if(!maze.isFree(x, y+1) && !maze.isFree(x, y-1) && maze.isFree(x+1, y) && maze.isFree(x-1, y)) return true;
        if(maze.isFree(x, y+1) && maze.isFree(x, y-1) && !maze.isFree(x+1, y) && !maze.isFree(x-1, y)) return true;
        return false;
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
    Position::maze.saveSolution("line");
    cv::waitKey(0);

}
