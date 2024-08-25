#include <vector>
#include <queue>
#include <iostream>
#include <climits>
#include <algorithm>
#include <random>
#include <bits/stdc++.h>
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

vector<int> Dijkstra(const vector<vector<int>>& graph, int src, vector<int>& pred) {
    int num_vertices = graph.size();
    vector<int> dist(num_vertices, INT_MAX);
    vector<bool> sptSet(num_vertices, false);
    
    dist[src] = 0;
    
    for (int count = 0; count < num_vertices - 1; count++) {
        int minDist = INT_MAX, u = -1;
        for (int i = 0; i < num_vertices; i++) {
            if (!sptSet[i] && dist[i] < minDist) {
                minDist = dist[i];
                u = i;
            }
        }
        if (u == -1) break;
        
        sptSet[u] = true;
        for (int v = 0; v < num_vertices; v++) {
            if (!sptSet[v] && graph[u][v] != INT_MAX && dist[u] != INT_MAX && dist[u] + graph[u][v] < dist[v]) {
                dist[v] = dist[u] + graph[u][v];
                pred[v] = u;
            }
        }
    }
    return dist;
}

vector<vector<Node>> findPaths(vector<string>& map, vector<Node>& starts, vector<Node>& ends) {
    vector<vector<int>> graph = createGraph(map);
    vector<vector<Node>> paths;
    
    for (int i = 0; i < starts.size(); i++) {
        int srcIndex = toIndex(starts[i].x, starts[i].y, map[0].size());
        int destIndex = toIndex(ends[i].x, ends[i].y, map[0].size());
        
        vector<int> pred(graph.size(), -1); 
        vector<int> dist = Dijkstra(graph, srcIndex, pred);
        
        vector<Node> path;
        if (dist[destIndex] == INT_MAX) {
            cout << "Path not found from (" << starts[i].x << "," << starts[i].y << ") to (" << ends[i].x << "," << ends[i].y << ")" << endl;
            continue;
        }
        
        int current = destIndex;
        while (current != srcIndex) {
            int x = current / map[0].size();
            int y = current % map[0].size();
            path.push_back({x, y});
            current = pred[current];
        }
        path.push_back(starts[i]);
        reverse(path.begin(), path.end());
        paths.push_back(path);
    }
    
    return paths;
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
    
    int numRobots = 10;
    
    simulateRobots(map, numRobots);
    
    return 0;
}
