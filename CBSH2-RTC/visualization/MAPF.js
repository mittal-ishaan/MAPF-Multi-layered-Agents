var map = "", map_h = 0, map_w = 0;
var paths = [];
var cnt = 0;
var animationStarted = false;
var animationInterval;
var robots = []; // Array to store robot elements for animation

function readMap(file) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var contents = e.target.result;
        if (contents[0] == 't') {
            var lines = e.target.result.split("\n");
            for (let i = 0; i < lines[1].length; i++) {
                let currentChar = lines[1].charAt(i);
                if (!isNaN(currentChar)) {
                    map_h *= 10;
                    map_h += currentChar - '0';
                }
            }
            for (let i = 0; i < lines[2].length; i++) {
                let currentChar = lines[2].charAt(i);
                if (!isNaN(currentChar)) {
                    map_w *= 10;
                    map_w += currentChar - '0';
                }
            }
            for (let i = 4; i < lines.length; i++) {
                map += lines[i];
            }
        } else {
            for (let i = 0; i < contents.length; i++) {
                let currentChar = contents.charAt(i);
                if (!isNaN(currentChar)) {
                    map_h *= 10;
                    map_h += currentChar - '0';
                } else if (currentChar == ',') {
                    i++;
                    for (; i < contents.length; i++) {
                        currentChar = contents.charAt(i);
                        if (currentChar === '\r') {
                            break;
                        }
                        if (currentChar === '\n') {
                            break;
                        }
                        if (!isNaN(currentChar)) {
                            map_w *= 10;
                            map_w += currentChar - '0';
                        }
                    }
                    for (let j = i; j < contents.length; j++) {
                        currentChar = contents.charAt(j);
                        if (currentChar === '\r' || currentChar === '\n') {
                            continue;
                        }
                        map += (currentChar);
                    }
                    break;
                }
            }
        }
        loadMap();
    };
    reader.readAsText(file);
}

var canvas;
var context;
var canvas_width, canvas_height;
var width, height;

function loadMap() {
    canvas = document.getElementById('myCanvas');
    context = canvas.getContext('2d');
    canvas_width = canvas.width;
    canvas_height = canvas.height;

    width = canvas_width / map_w;
    height = canvas_height / map_h;
    for (let i = 0; i < map_w; i++) {
        for (let j = 0; j < map_h; j++) {
            let x = j * width;
            let y = i * height;
            if (map[i * map_w + j] == '.') {
                context.fillStyle = '#e0e0e0'; // Light grey for open spaces
            } else if (map[i * map_w + j] == '@') {
                context.fillStyle = '#000000'; // Black for obstacles
            } else if (map[i * map_w + j] == 'T') {
                context.fillStyle = '#333333'; // Dark grey for targets
            } else {
                continue;
            }
            context.fillRect(x, y, 0.95 * width, 0.95 * height);
        }
    }
}

var canvas1;
var context1;
var pathsColors = [];

function drawPath(x, y, path, color) {
    context1.strokeStyle = color;
    context1.lineWidth = 2; // Increased line width for better visibility
    context1.beginPath();
    context1.moveTo(y * width + width / 2, x * height + height / 2);
    for (let i = 0; i < path.length; i += 2) {
        let x1 = path[i] * width + width / 2;
        let y1 = path[i + 1] * height + height / 2;
        context1.lineTo(y1, x1);
    }
    context1.stroke();
}

function move(x, y, state, agent, color) {
    context1.fillStyle = color;
    context1.fillRect(y * width, x * height, 0.95 * width, 0.95 * height);
    context1.fillStyle = "#ffffff"; // White text for better contrast
    context1.font = "bold 14px Arial"; // Changed font size and weight for clarity
    context1.textAlign = "center";
    context1.textBaseline = "middle";
    context1.fillText(agent.toString(), y * width + width / 2, x * height + height / 2);
}

function updatePaths(j) {
    context1.clearRect(0, 0, canvas1.width, canvas1.height);
    for (let i = 0; i < paths.length; i++) {
        if (j >= paths[i].length) {
            move(paths[i][paths[i].length - 3], paths[i][paths[i].length - 2], 1, i, pathsColors[i]);
        } else {
            move(paths[i][j], paths[i][j + 1], 0, i, pathsColors[i]);
            let remainingPath = paths[i].slice(j + 2);
            drawPath(paths[i][j], paths[i][j + 1], remainingPath, pathsColors[i]);
        }
    }
}

function solve(j) {
    updatePaths(j);
}

function draw() {
    canvas1 = document.getElementById('myCanvas1');
    context1 = canvas1.getContext('2d');
    var max_len = 0;
    for (let i = 0; i < paths.length; i++) {
        max_len = Math.max(max_len, paths[i].length);
        pathsColors[i] = getRandomColor(); // Assign unique color to each path

        // Create and store robot elements
        robots[i] = {
            x: paths[i][0] * width,
            y: paths[i][1] * height,
            element: context1
        };
    }
}

function getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function handleFileSelect(event) {
    var file = event.target.files[0];
    var reader = new FileReader();
    reader.onload = function(event) {
        var csvData = event.target.result;
        processData(csvData);
        draw();
    };
    reader.readAsText(file);
}

function processData(csvData) {
    var lines = csvData.split("\n");
    for (var i = 0; i < lines.length; i++) {
        var idx = lines[i].indexOf(":");
        var str = lines[i].substring(idx + 2);
        var values = str.split("->");
        var p = [];
        if (values.length > 1) {
            for (let j = 0; j < values.length; j++) {
                var x = 0;
                for (let k = 1; k < values[j].length - 1; k++) {
                    if (values[j][k] === ',') {
                        p.push(x);
                        x = 0;
                        continue;
                    }
                    x *= 10;
                    x += values[j][k] - '0';
                }
                p.push(x);
            }
            paths.push(p);
        }
    }
}

function startAnimation() {
    if (!animationStarted) {
        animationStarted = true;
        animationInterval = setInterval(function() {
            if (cnt >= paths[0].length) { // Assuming all paths are of the same length
                clearInterval(animationInterval);
                return;
            }
            solve(cnt);
            cnt += 2;
            animateRobots(cnt);
        }, 1000); // Adjust the speed here (in milliseconds)
    }
}

function animateRobots(j) {
    for (let i = 0; i < robots.length; i++) {
        if (j >= paths[i].length) {
            // Move to final position
            gsap.to(robots[i].element, {
                duration: 1,
                x: paths[i][paths[i].length - 3] * width,
                y: paths[i][paths[i].length - 2] * height,
                ease: "power1.inOut"
            });
        } else {
            // Move along the path
            gsap.to(robots[i].element, {
                duration: 1,
                x: paths[i][j] * width,
                y: paths[i][j + 1] * height,
                ease: "power1.inOut"
            });
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', function(e) {
        var file = e.target.files[0];
        readMap(file);
    });
    var csvInput = document.getElementById('csvFileInput');
    csvInput.addEventListener('change', function(e) {
        handleFileSelect(e);
    });
    var button = document.getElementById("myButton");

    button.addEventListener("click", function() {
        if (!animationStarted) {
            startAnimation();
        }
    });
});
