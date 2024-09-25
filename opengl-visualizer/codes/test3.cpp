#include <vector>
#include <queue>
#include <iostream>
#include <climits>
#include <algorithm>
#include <random>
#include <set>
#include <tuple>
#include <unordered_map>
#include <cfloat>

using namespace std;

struct Node {
    int x, y;
    bool operator==(const Node& other) const {
        return x == other.x && y == other.y;
    }
};

int toIndex(int x, int y, int width) {
    return x * width + y;
}

bool isValid(int x, int y, vector<string>& map) {
    return (x >= 0 && x < map.size() && y >= 0 && y < map[0].size() && map[x][y] == '.');
}

vector<vector<int>> createGraph(vector<string>& map) {
    int height = map.size();
    int width = map[0].size();
    vector<vector<int>> graph(height * width, vector<int>(height * width, INT_MAX));

    vector<pair<int, int>> directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (map[i][j] == '.') {
                int u = toIndex(i, j, width);
                for (auto dir : directions) {
                    int newX = i + dir.first;
                    int newY = j + dir.second;
                    if (isValid(newX, newY, map)) {
                        int v = toIndex(newX, newY, width);
                        graph[u][v] = 1; 
                    }
                }
            }
        }
    }
    return graph;
}

vector<Node> highwayAlgorithm(vector<vector<int>>& graph, Node start, Node goal, vector<string>& map, unordered_map<int, set<int>>& constraints, double w) {
    int width = map[0].size();
    int height = map.size();
    
    int startIdx = toIndex(start.x, start.y, width);
    int goalIdx = toIndex(goal.x, goal.y, width);
    
    vector<int> gScore(graph.size(), INT_MAX);
    vector<double> fScore(graph.size(), DBL_MAX); 
    vector<int> cameFrom(graph.size(), -1);
    set<int> openSet;
    
    gScore[startIdx] = 0;
    fScore[startIdx] = abs(start.x - goal.x) + abs(start.y - goal.y);
    openSet.insert(startIdx);
    
    while (!openSet.empty()) {
        int current = *openSet.begin();
        for (auto it = openSet.begin(); it != openSet.end(); ++it) {
            if (fScore[*it] < fScore[current]) {
                current = *it;
            }
        }

        if (current == goalIdx) {
            vector<Node> path;
            while (current != startIdx) {
                int x = current / width;
                int y = current % width;
                path.push_back({x, y});
                current = cameFrom[current];
            }
            path.push_back(start);
            reverse(path.begin(), path.end());
            return path;
        }

        openSet.erase(current);
        int x = current / width;
        int y = current % width;

        vector<pair<int, int>> directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
        for (auto& dir : directions) {
            int newX = x + dir.first;
            int newY = y + dir.second;
            if (isValid(newX, newY, map)) {
                int neighbor = toIndex(newX, newY, width);
                int tentative_gScore = gScore[current] + 1;

                if (tentative_gScore < gScore[neighbor] && constraints[neighbor].find(tentative_gScore) == constraints[neighbor].end()) {
                    cameFrom[neighbor] = current;
                    gScore[neighbor] = tentative_gScore;
                    fScore[neighbor] = gScore[neighbor] + w * (abs(newX - goal.x) + abs(newY - goal.y));
                    openSet.insert(neighbor);
                }
            }
        }
    }
    return {}; 
}

tuple<int, int, int> validate(const vector<vector<Node>>& paths) {
    for (int t = 0; t < paths[0].size(); ++t) {
        for (int i = 0; i < paths.size(); ++i) {
            for (int j = i + 1; j < paths.size(); ++j) {
                if (paths[i][t] == paths[j][t]) {
                    return {i, j, t}; 
                }
                if (t > 0 && paths[i][t] == paths[j][t-1] && paths[j][t] == paths[i][t-1]) {
                    return {i, j, t}; 
                }
            }
        }
    }
    return {-1, -1, -1}; 
}

vector<vector<Node>> CBS(vector<string>& map, vector<Node>& starts, vector<Node>& ends, double w = 1.0) {
    vector<vector<int>> graph = createGraph(map);
    unordered_map<int, set<int>> constraints;
    vector<vector<Node>> paths;

    for (int i = 0; i < starts.size(); i++) {
        vector<Node> path = highwayAlgorithm(graph, starts[i], ends[i], map, constraints, w);
        if (!path.empty()) {
            paths.push_back(path);
        } else {
            cout << "Path not found from (" << starts[i].x << "," << starts[i].y << ") to (" << ends[i].x << "," << ends[i].y << ")" << endl;
            return {};
        }
    }

    while (true) {
        auto [ai, aj, t] = validate(paths);
        if (ai == -1 && aj == -1) {
            return paths; 
        }

        constraints[toIndex(paths[ai][t].x, paths[ai][t].y, map[0].size())].insert(t);
        paths[ai] = highwayAlgorithm(graph, starts[ai], ends[ai], map, constraints, w);

        if (paths[ai].empty()) {
            cout << "No valid path for robot " << ai << " due to constraints." << endl;
            return {};
        }
    }
}

void printPaths(const vector<vector<Node>>& paths) {
    int max_time = 0;
    vector<vector<Node>> paths_padded(paths.size());

    for (const auto& path : paths) {
        max_time = max(max_time, (int)path.size());
    }

    for (int i = 0; i < paths.size(); ++i) {
        paths_padded[i] = paths[i];
        if (paths[i].size() < max_time) {
            Node last_position = paths[i].back();
            while (paths_padded[i].size() < max_time) {
                paths_padded[i].push_back(last_position);
            }
        }
    }

    for (int t = 0; t < max_time; ++t) {
        cout << t << ":";
        for (int i = 0; i < paths_padded.size(); ++i) {
            cout << "(" << paths_padded[i][t].y << "," << paths_padded[i][t].x << "),";
        }
        cout << endl;
    }
}

void simulateRobots(vector<string>& map, int numRobots) {
    vector<Node> starts, ends;
    vector<Node> freeCells;

    for (int i = 0; i < map.size(); i++) {
        for (int j = 0; j < map[0].size(); j++) {
            if (map[i][j] == '.') {
                freeCells.push_back({i, j});
            }
        }
    }

    random_device rd;
    mt19937 g(rd());
    shuffle(freeCells.begin(), freeCells.end(), g);

    for (int i = 0; i < numRobots; i++) {
        starts.push_back(freeCells[i]);
        ends.push_back(freeCells[numRobots + i]);
    }

    vector<vector<Node>> paths = CBS(map, starts, ends, 1.5); 
    if (!paths.empty()) {
        printPaths(paths);
    }
}

int main() {
    vector<string> map = {
        ".................",
        ".@@@@@@@.@@@@@@@.",
        ".@@@@@@@.@@@@@@@.",
        ".................",
        ".@@@@@@@.@@@@@@@.",
        ".@@@@@@@.@@@@@@@.",
        ".................",
        ".@@@@@@@.@@@@@@@.",
        ".@@@@@@@.@@@@@@@.",
        "................."
    };

    int numRobots = 5;

    simulateRobots(map, numRobots);

    return 0;
}
