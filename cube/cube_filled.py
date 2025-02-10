import math
import time
import os
import argparse

def clear_screen():
    """Clears the terminal screen using ANSI escape codes (xterm compatible)."""
    print('\x1b[2J\x1b[H', end='')

def rotate_x(point, angle):
    """Rotates a 3D point around the x-axis."""
    x, y, z = point
    rad = math.radians(angle)
    cos_rad = math.cos(rad)
    sin_rad = math.sin(rad)
    return (x, y * cos_rad - z * sin_rad, y * sin_rad + z * cos_rad)

def rotate_y(point, angle):
    """Rotates a 3D point around the y-axis."""
    x, y, z = point
    rad = math.radians(angle)
    cos_rad = math.cos(rad)
    sin_rad = math.sin(rad)
    return (x * cos_rad + z * sin_rad, y, -x * sin_rad + z * cos_rad)

def rotate_z(point, angle):
    """Rotates a 3D point around the z-axis."""
    x, y, z = point
    rad = math.radians(angle)
    cos_rad = math.cos(rad)
    sin_rad = math.sin(rad)
    return (x * cos_rad - y * sin_rad, x * sin_rad + y * cos_rad, z)

def project_point(point, screen_width, screen_height, zoom=10, offset_x=0, offset_y=0):
    """Projects a 3D point to 2D screen coordinates."""
    x, y, z = point
    factor = zoom / (z + zoom)
    x_2d = int(screen_width / 2 + offset_x + factor * x * screen_width / 2)
    y_2d = int(screen_height / 2 + offset_y - factor * y * screen_height / 2)
    return (x_2d, y_2d)

def normalize_vector(vec):
    """Normalizes a 3D vector to unit length."""
    x, y, z = vec
    magnitude = math.sqrt(x*x + y*y + z*z)
    if magnitude == 0:
        return (0, 0, 0)  # Avoid division by zero
    return (x/magnitude, y/magnitude, z/magnitude)

def cross_product(vec1, vec2):
    """Calculates the cross product of two 3D vectors."""
    x1, y1, z1 = vec1
    x2, y2, z2 = vec2
    return (y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2)

def calculate_normal(face_vertices):
    """Calculates the normal vector of a face (assuming vertices are in order)."""
    p1, p2, p3 = face_vertices[0], face_vertices[1], face_vertices[2] # Using first three vertices to define plane
    vec1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    vec2 = (p3[0] - p1[0], p3[1] - p1[1], p2[2] - p1[2]) # Corrected vec2 to use p2 instead of p3 for consistent plane definition from p1
    normal = cross_product(vec1, vec2)
    return normalize_vector(normal)

def draw_filled_polygon(screen, points_2d, draw_char):
    """Draws a filled polygon on the screen buffer (basic scanline fill)."""
    if not points_2d or len(points_2d) < 3:
        return

    min_y = min(p[1] for p in points_2d)
    max_y = max(p[1] for p in points_2d)

    for y in range(min_y, max_y + 1):
        intersections = []
        for i in range(len(points_2d)):
            p1 = points_2d[i]
            p2 = points_2d[(i + 1) % len(points_2d)]

            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):  # Edge intersects scanline
                if p1[1] != p2[1]: # Avoid division by zero for horizontal lines
                    intersection_x = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                    intersections.append(int(intersection_x))

        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start = intersections[i]
            x_end = intersections[i+1] if i+1 < len(intersections) else screen_width

            for x in range(max(0, x_start), min(screen_width, x_end + 1)):
                if 0 <= y < screen_height:
                    screen[y][x] = draw_char


def draw_cube(screen, vertices, faces, screen_width, screen_height, rotation_angles, shading_levels, zoom_level, light_direction):
    """Draws the filled and shaded cube on the screen buffer using gradient map."""

    rotated_vertices = []
    for vertex in vertices:
        rotated_vertex = vertex
        rotated_vertex = rotate_x(rotated_vertex, rotation_angles[0])
        rotated_vertex = rotate_y(rotated_vertex, rotation_angles[1])
        rotated_vertex = rotate_z(rotated_vertex, rotation_angles[2])
        rotated_vertices.append(rotated_vertex)

    projected_vertices = [project_point(v, screen_width, screen_height, zoom=zoom_level) for v in rotated_vertices]

    face_depths = []
    for face in faces:
        face_vertices_3d = [rotated_vertices[v_index] for v_index in face]
        face_normal = calculate_normal(face_vertices_3d)

        # Calculate light intensity using dot product of face normal and light direction
        intensity = max(0, sum(n * l for n, l in zip(face_normal, light_direction))) # Clamp to 0 (no negative light)

        face_depths.append((sum(v[2] for v in face_vertices_3d) / len(face_vertices_3d), face, intensity)) # Store depth and intensity


    face_depths.sort(key=lambda item: item[0], reverse=True) # Sort back to front


    for avg_z, face, intensity in face_depths:
        if avg_z < 0: # Basic back-face culling
            continue

        face_vertices_2d = [projected_vertices[v_index] for v_index in face]

        # Determine shading character based on light intensity using REVERSED gradient map
        shade_index = int(intensity * (len(shading_levels) - 1))
        shade_index = max(0, min(shade_index, len(shading_levels) - 1))
        # **REVERSED INDEXING to use darkest characters for lower intensity (less light)**
        draw_char = shading_levels[len(shading_levels) - 1 - shade_index] # Reverse index to map intensity to dark-to-light gradient


        draw_filled_polygon(screen, face_vertices_2d, draw_char)


def initialize_screen(width, height):
    """Creates an empty screen buffer."""
    return [[' ' for _ in range(width)] for _ in range(height)]

def display_screen(screen):
    """Prints the screen buffer to the terminal."""
    for row in screen:
        print("".join(row))

def parse_arguments():
    """Parses command line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="""Rotate a 3D cube in the terminal using ASCII with gradient shading.

        This script visualizes a rotating 3D filled and shaded cube using ASCII characters,
        now with proper shading using a gradient map from light to dark.
        Customize size, rotation speed, shading gradient, perspective, and light direction.
        """
    )
    parser.add_argument('--width', '-w', type=int, default=60,
                        help='Screen width in characters (default: 60).')
    parser.add_argument('--height', '-H', type=int, default=30,
                        help='Screen height in characters (default: 30).')
    parser.add_argument('--x_speed', '--xs', type=float, default=1.0,
                        help='Rotation speed around X-axis (default: 1.0).')
    parser.add_argument('--y_speed', '--ys', type=float, default=1.5,
                        help='Rotation speed around Y-axis (default: 1.5).')
    parser.add_argument('--z_speed', '--zs', type=float, default=0.7,
                        help='Rotation speed around Z-axis (default: 0.7).')
    parser.add_argument('--zoom', '-z', type=int, default=10,
                        help='Zoom level (perspective, default: 10).')
    # **REVERSED DEFAULT GRADIENT - DARKEST LAST**
    parser.add_argument('--shading', '-s', type=str, default='.,-~+=*#@',
                        help='Shading gradient characters (lightest to darkest, default: ".,-~+=*#@").')
    parser.add_argument('--light_x', type=float, default=1.0, help='X component of light direction (default: 1.0).')
    parser.add_argument('--light_y', type=float, default=1.0, help='Y component of light direction (default: 1.0).')
    parser.add_argument('--light_z', type=float, default=-1.0, help='Z component of light direction (default: -1.0). Negative Z is towards the viewer.')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    screen_width = args.width
    screen_height = args.height

    # Define cube vertices (smaller cube)
    vertices = [
        (-0.5, -0.5, -0.5), # 0: Back lower left
        ( 0.5, -0.5, -0.5), # 1: Back lower right
        ( 0.5,  0.5, -0.5), # 2: Back upper right
        (-0.5,  0.5, -0.5), # 3: Back upper left
        (-0.5, -0.5,  0.5), # 4: Front lower left
        ( 0.5, -0.5,  0.5), # 5: Front lower right
        ( 0.5,  0.5,  0.5), # 6: Front upper right
        (-0.5,  0.5,  0.5)  # 7: Front upper left
    ]

    # Define cube faces (vertex indices, COUNTER-CLOCKWISE ORDER for normals to point outwards)
    faces = [
        [0, 3, 2, 1], # Back face
        [4, 5, 6, 7], # Front face
        [3, 7, 6, 2], # Top face
        [0, 1, 5, 4], # Bottom face
        [0, 4, 7, 3], # Left face
        [1, 2, 6, 5]  # Right face
    ]

    shading_levels = list(args.shading) # Use characters provided by user, or default
    rotation_angles = [0, 0, 0]
    rotation_speed = [args.x_speed, args.y_speed, args.z_speed]
    zoom_level = args.zoom
    light_direction = normalize_vector((args.light_x, args.light_y, args.light_z))

    while True:
        screen = initialize_screen(screen_width, screen_height)
        draw_cube(screen, vertices, faces, screen_width, screen_height, rotation_angles, shading_levels, zoom_level, light_direction)
        clear_screen()
        display_screen(screen)

        for i in range(3):
            rotation_angles[i] += rotation_speed[i]
            rotation_angles[i] %= 360

        time.sleep(0.03)

