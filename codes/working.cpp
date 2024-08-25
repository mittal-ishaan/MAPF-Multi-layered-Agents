#include <vector>
#include <queue>
#include <iostream>
#include <climits>
#include <algorithm>
#include <random>
#include <cmath>
#include <unordered_map>
using namespace std;

struct Node {
    int x, y, t;
    Node(int x = 0, int y = 0, int t=0) : x(x), y(y), t(t) {}
    bool operator==(const Node& other) const {
        return x == other.x && y == other.y;
    }
    bool operator<(const Node& other) const {
        return tie(x, y) < tie(other.x, other.y);
    }
};

namespace std {
    template <>
    struct hash<Node> {
        size_t operator()(const Node& n) const {
            return hash<int>()(n.x) ^ (hash<int>()(n.y) << 1);
        }
    };
}

int toIndex(int x, int y, int width) {
    return x * width + y;
}

bool isValid(int x, int y, const vector<string>& map) {
    return (x >= 0 && x < map.size() && y >= 0 && y < map[0].size() && map[x][y] == '.');
}

vector<vector<int>> createGraph(const vector<string>& map) {
    int height = map.size();
    int width = map[0].size();
    vector<vector<int>> graph(height * width, vector<int>(height * width, INT_MAX));
    
    vector<pair<int, int>> directions = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};
    
    for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
            if (map[i][j] == '.') {
                int u = toIndex(i, j, width);
                for (const auto& dir : directions) {
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

int heuristic(const Node& a, const Node& b) {
    return abs(a.x - b.x) + abs(a.y - b.y);
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

vector<Node> AStar(vector<vector<int>>& graph, int src, int dest, const vector<string>& map) {
    int num_vertices = graph.size();
    vector<int> g_score(num_vertices, INT_MAX);
    vector<int> f_score(num_vertices, INT_MAX);
    vector<int> pred(num_vertices, -1);
    vector<bool> closed_set(num_vertices, false);
    
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> open_set;
    
    int map_size = map[0].size();
    
    g_score[src] = 0;
    f_score[src] = heuristic({src / map_size, src % map_size}, {dest / map_size, dest % map_size});
    open_set.push({f_score[src], src});
    
    while (!open_set.empty()) {
        int current = open_set.top().second;
        open_set.pop();
        
        if (current == dest) {
            vector<Node> path;
            while (pred[current] != -1) {
                path.push_back(Node(current / map_size, current % map_size));
                current = pred[current];
            }
            path.push_back(Node(src / map_size, src % map_size));
            reverse(path.begin(), path.end());
            return path;
        }
        
        closed_set[current] = true;
        for (int v = 0; v < num_vertices; v++) {
            if (graph[current][v] != INT_MAX && !closed_set[v]) {
                int tentative_g_score = g_score[current] + graph[current][v];
                if (tentative_g_score < g_score[v]) {
                    pred[v] = current;
                    g_score[v] = tentative_g_score;
                    f_score[v] = g_score[v] + heuristic(Node(v / map_size, v % map_size), Node(dest / map_size, dest % map_size));
                    open_set.push({f_score[v], v});
                }
            }
        }
    }
    return {};
}

vector<vector<Node>> findPaths(vector<string>& map, const vector<Node>& starts, const vector<Node>& ends) {
    vector<vector<int>> graph = createGraph(map);
    vector<vector<Node>> paths;
    
    for (int i = 0; i < starts.size(); i++) {
        int srcIndex = toIndex(starts[i].x, starts[i].y, map[0].size());
        int destIndex = toIndex(ends[i].x, ends[i].y, map[0].size());
        
        vector<Node> path = AStar(graph, srcIndex, destIndex, map);
        
        if (path.empty()) {
            cout << "Path not found from (" << starts[i].x << "," << starts[i].y << ") to (" << ends[i].x << "," << ends[i].y << ")" << endl;
            continue;
        }
        
        // Mark the path as unidirectional
        for (int j = 0; j < path.size() - 1; j++) {
            int from = toIndex(path[j].x, path[j].y, map[0].size());
            int to = toIndex(path[j + 1].x, path[j + 1].y, map[0].size());
            graph[to][from] = INT_MAX;
        }
        
        paths.push_back(path);
    }
    
    return paths;
}

void simulateRobots(vector<string>& map, int numRobots) {
    vector<Node> starts, ends;
    vector<Node> freeCells;
    
    for (int i = 0; i < map.size(); i++) {
        for (int j = 0; j < map[0].size(); j++) {
            if (map[i][j] == '.') {
                freeCells.push_back(Node(i, j));
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
    
    vector<vector<Node>> paths = findPaths(map, starts, ends);
    printPaths(paths);
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
    
    int numRobots = 20;
    
    simulateRobots(map, numRobots);
    
    return 0;
}
