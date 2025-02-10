document.addEventListener('DOMContentLoaded', () => {
    const asciiScreen = document.getElementById('asciiScreen');
    const screenWidth = 60;  // Adjust for ASCII display, keep it relatively narrow
    const screenHeight = 30; // Adjust for ASCII display

    const vertices = [
        [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
        [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5]
    ];

    const faces = [
        [0, 3, 2, 1], [4, 5, 6, 7], [3, 7, 6, 2],
        [0, 1, 5, 4], [0, 4, 7, 3], [1, 2, 6, 5]
    ];

    const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ];

    const lightDirection = normalizeVector([1.0, 1.0, -1.0]);
    console.log("Initial lightDirection:", lightDirection); // Add this line

    const shades = ['.', '-', '#']; // Shading characters
    const outlineChar = '*';       // Outline character

    let rotationAngles = [0, 0, 0];
    const rotationSpeed = [1.0, 1.5, 0.7];
    const zoomLevel = 10;
    const lightDirection = normalizeVector([1.0, 1.0, -1.0]);


    let screenBuffer = initializeScreen(screenWidth, screenHeight); // Initialize screen buffer


    function rotateX(point, angle) { /* ... (same as before) ... */ }
    function rotateY(point, angle) { /* ... (same as before) ... */ }
    function rotateZ(point, angle) { /* ... (same as before) ... */ }
    function projectPoint(point, screenWidth, screenHeight, zoom = 10, offsetX = 0, offsetY = 0) { /* ... (same as before) ... */ }
    function normalizeVector(vec) { /* ... (same as before) ... */ }
    function crossProduct(vec1, vec2) { /* ... (same as before) ... */ }
    function calculateNormal(faceVertices) {
        if (!faceVertices || faceVertices.length < 3) {
            console.warn("calculateNormal: Invalid faceVertices input:", faceVertices); // Log invalid input
            return [0, 0, 0]; // Return a default normal (zero vector)
        }
        const [p1, p2, p3] = faceVertices;
        if (!p1 || !p2 || !p3) {
            console.warn("calculateNormal: Undefined vertex in faceVertices:", faceVertices); // Log if any vertex is undefined
            return [0, 0, 0]; // Return default normal
        }
        const vec1 = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
        const vec2 = [p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]];
        return normalizeVector(crossProduct(vec1, vec2));
    }
    function initializeScreen(width, height) {
        return Array(height).fill(null).map(() => Array(width).fill(' '));
    }
        function drawLine(screen, point1_2d, point2_2d, drawChar, screenWidth, screenHeight) {
        // Very basic line drawing with ASCII chars (similar to your Python version)
        let x1 = Math.round(point1_2d[0]);
        let y1 = Math.round(point1_2d[1]);
        let x2 = Math.round(point2_2d[0]);
        let y2 = Math.round(point2_2d[1]);

        if (! (0 <= x1 < screenWidth && 0 <= y1 < screenHeight && 0 <= x2 < screenWidth && 0 <= y2 < screenHeight)) {
            return;
        }

        if (x1 === x2) { // Vertical line
            for (let y = Math.min(y1, y2); y <= Math.max(y1, y2); y++) {
                if (0 <= y < screenHeight) screen[y][x1] = drawChar;
            }
        } else if (y1 === y2) { // Horizontal line
            for (let x = Math.min(x1, x2); x <= Math.max(x1, x2); x++) {
                if (0 <= x < screenWidth) screen[y1][x] = drawChar;
            }
        } else { // Diagonal-ish line (very basic)
            const dx = Math.abs(x2 - x1);
            const dy = Math.abs(y2 - y1);
            const sx = (x1 < x2) ? 1 : -1;
            const sy = (y1 < y2) ? 1 : -1;
            let err = dx - dy;
            let x = x1;
            let y = y1;

            while (true) {
                if (0 <= x < screenWidth && 0 <= y < screenHeight) screen[y][x] = drawChar;
                if (x === x2 && y === y2) break;
                const e2 = 2 * err;
                if (e2 > -dy) { err -= dy; x += sx; }
                if (e2 < dx) { err += dx; y += sy; }
            }
        }
    }


    function drawFilledPolygon(screen, points_2d, drawChar, screenWidth, screenHeight) {
        // Basic scanline fill for ASCII (approximate)
        if (!points_2d || points_2d.length < 3) return;

        let min_y = Math.min(...points_2d.map(p => p[1]));
        let max_y = Math.max(...points_2d.map(p => p[1]));

        for (let y = min_y; y <= max_y; y++) {
            let intersections = [];
            for (let i = 0; i < points_2d.length; i++) {
                const p1 = points_2d[i];
                const p2 = points_2d[(i + 1) % points_2d.length];

                if ((p1[1] <= y && y < p2[1]) || (p2[1] <= y && y < p1[1])) {
                    if (p1[1] !== p2[1]) {
                        const intersection_x = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0];
                        intersections.push(intersection_x);
                    }
                }
            }
            intersections.sort((a, b) => a - b);
            for (let i = 0; i < intersections.length; i += 2) {
                let x_start = Math.ceil(intersections[i]);
                let x_end = Math.floor(intersections[i + 1] || screenWidth); // Use screenWidth if no pair

                for (let x = Math.max(0, x_start); x <= Math.min(screenWidth - 1, x_end); x++) {
                    if (0 <= y && y < screenHeight) screen[Math.round(y)][x] = drawChar;
                }
            }
        }
    }


    function drawCube(screen, vertices, faces, edges, screenWidth, screenHeight, rotationAngles, shades, zoomLevel, lightDirection, outlineChar) {
        const rotatedVertices = vertices.map(vertex => { /* ... (same as before) ... */ return rotateZ(rotateY(rotateX(vertex, rotationAngles[0]), rotationAngles[1]), rotationAngles[2]); });
        const projectedVertices = rotatedVertices.map(v => projectPoint(v, screenWidth, screenHeight, zoomLevel));

        const faceDepths = [];
        faces.forEach(face => {
            const faceVertices3d = face.map(vIndex => rotatedVertices[vIndex]);
            const faceNormal = calculateNormal(faceVertices3d);
            const intensity = Math.max(0, faceNormal.reduce((sum, n, i) => sum + n * lightDirection[i], 0));
            const avgZ = faceVertices3d.reduce((sum, v) => sum + v[2], 0) / faceVertices3d.length;
            faceDepths.push([avgZ, face, intensity]);
        });

        faceDepths.sort((a, b) => b[0] - a[0]);

        faceDepths.forEach(([avgZ, face, intensity]) => {
            if (avgZ < 0) return;

            const faceVertices2d = face.map(vIndex => projectedVertices[vIndex]);

            let drawChar;
            if (intensity > 2.0/3.0) {
                drawChar = shades[0]; // Brightest shade
            } else if (intensity > 1.0/3.0) {
                drawChar = shades[1]; // Neutral shade
            } else {
                drawChar = shades[2]; // Darkest shade
            }
            drawFilledPolygon(screen, faceVertices2d, drawChar, screenWidth, screenHeight);
        });

        // Draw Outlines after filling faces
        const projectedEdges = edges.map(edge => edge.map(vIndex => projectedVertices[vIndex]));
        projectedEdges.forEach(edgePoints2d => {
            drawLine(screen, edgePoints2d[0], edgePoints2d[1], outlineChar, screenWidth, screenHeight);
        });
    }


    function clearScreen(screen) {
        for (let y = 0; y < screenHeight; y++) {
            for (let x = 0; x < screenWidth; x++) {
                screen[y][x] = ' '; // Fill screen with spaces
            }
        }
    }


    function animate() {
        clearScreen(screenBuffer); // Clear the screen buffer
        drawCube(screenBuffer, vertices, faces, edges, screenWidth, screenHeight, rotationAngles, shades, zoomLevel, lightDirection, outlineChar);
        displayScreen(screenBuffer); // Update <pre> with screen buffer content

        for (let i = 0; i < 3; i++) {
            rotationAngles[i] += rotationSpeed[i];
            rotationAngles[i] %= 360;
        }

        setTimeout(animate, 30); // Use setTimeout for animation loop (adjust delay as needed)
    }

    animate(); // Start animation
});

