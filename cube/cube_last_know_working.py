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
        return (0, 0, 0)
    return (x/magnitude, y/magnitude, z/magnitude)

def cross_product(vec1, vec2):
    """Calculates the cross product of two 3D vectors."""
    x1, y1, z1 = vec1
    x2, y2, z2 = vec2
    return (y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2)

def calculate_normal(face_vertices):
    """Calculates the normal vector of a face."""
    p1, p2, p3 = face_vertices[0], face_vertices[1], face_vertices[2]
    vec1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    vec2 = (p3[0] - p1[0], p3[1] - p1[1], p2[2] - p1[2])
    normal = cross_product(vec1, vec2)
    return normalize_vector(normal)

def draw_line(screen, point1_2d, point2_2d, draw_char, screen_width, screen_height):
    """Draws a basic line on the screen buffer."""
    x1, y1 = point1_2d
    x2, y2 = point2_2d

    if not (0 <= x1 < screen_width and 0 <= y1 < screen_height and 0 <= x2 < screen_width and 0 <= y2 < screen_height):
        return

    if x1 == x2: # Vertical line
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= y < screen_height:
                screen[y][x1] = draw_char
    elif y1 == y2: # Horizontal line
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < screen_width:
                screen[y1][x] = draw_char
    else: # Diagonal-ish line (very basic)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1
        while True:
            if 0 <= x < screen_width and 0 <= y < screen_height:
                screen[y][x] = draw_char
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy


def draw_filled_polygon(screen, points_2d, draw_char, screen_width, screen_height):
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

            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                if p1[1] != p2[1]:
                    intersection_x = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                    intersections.append(int(intersection_x))

        intersections.sort()
        for i in range(0, len(intersections), 2):
            x_start = intersections[i]
            x_end = intersections[i+1] if i+1 < len(intersections) else screen_width

            for x in range(max(0, x_start), min(screen_width, x_end + 1)):
                if 0 <= y < screen_height:
                    screen[y][x] = draw_char


def draw_cube(screen, vertices, faces, edges, screen_width, screen_height, rotation_angles, shades, zoom_level, light_direction, outline_char):
    """Draws the filled, shaded, and outlined cube on the screen buffer."""

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
        intensity = max(0, sum(n * l for n, l in zip(face_normal, light_direction)))
        face_depths.append((sum(v[2] for v in face_vertices_3d) / len(face_vertices_3d), face, intensity))

    face_depths.sort(key=lambda item: item[0], reverse=True)

    for avg_z, face, intensity in face_depths:
        if avg_z < 0: # Back-face culling
            continue

        face_vertices_2d = [projected_vertices[v_index] for v_index in face]

        # 3-Shade gradient mapping
        if intensity > 2.0/3.0: # Brightest third
            draw_char = shades[0]
        elif intensity > 1.0/3.0: # Middle third
            draw_char = shades[1]
        else:                   # Darkest third
            draw_char = shades[2]

        draw_filled_polygon(screen, face_vertices_2d, draw_char, screen_width, screen_height)

    # Draw Outlines after filling faces
    projected_edges = []
    for edge in edges:
        v1_index, v2_index = edge
        projected_edges.append((projected_vertices[v1_index], projected_vertices[v2_index]))

    for edge_points_2d in projected_edges:
        draw_line(screen, edge_points_2d[0], edge_points_2d[1], outline_char, screen_width, screen_height)


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
        description="""Rotate a 3D cube in the terminal using ASCII, shaded with outlines.

        This script visualizes a rotating 3D filled, shaded, and outlined cube using ASCII.
        It offers 3-level shading and customizable outline.
        Customize size, rotation, shading levels, outline character, perspective, and light.
        """
    )
    parser.add_argument('--width', '-w', type=int, default=60, help='Screen width.')
    parser.add_argument('--height', '-H', type=int, default=30, help='Screen height.')
    parser.add_argument('--x_speed', '--xs', type=float, default=1.0, help='Rotation speed around X-axis.')
    parser.add_argument('--y_speed', '--ys', type=float, default=1.5, help='Rotation speed around Y-axis.')
    parser.add_argument('--z_speed', '--zs', type=float, default=0.7, help='Rotation speed around Z-axis.')
    parser.add_argument('--zoom', '-z', type=int, default=10, help='Zoom level (perspective).')
    parser.add_argument('--shades', type=str, default='.-#', # 3 shades default
                        help='Shading characters (light, neutral, dark - e.g., ".-#").')
    parser.add_argument('--light_x', type=float, default=1.0, help='Light X direction.')
    parser.add_argument('--light_y', type=float, default=1.0, help='Light Y direction.')
    parser.add_argument('--light_z', type=float, default=-1.0, help='Light Z direction.')
    parser.add_argument('--outline_char', '-o', type=str, default='*', help='Character for cube outline (default: "*").')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    screen_width = args.width
    screen_height = args.height

    vertices = [ # Smaller cube vertices
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5)
    ]

    faces = [ # Face vertex indices (counter-clockwise)
        [0, 3, 2, 1], [4, 5, 6, 7], [3, 7, 6, 2],
        [0, 1, 5, 4], [0, 4, 7, 3], [1, 2, 6, 5]
    ]

    edges = [ # Cube edges (vertex index pairs)
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ] # Corrected edges definition with closing parenthesis and comma


    shades = list(args.shades) # 3 shading levels
    if len(shades) != 3:
        print("Warning: Shading argument should provide exactly 3 characters. Using default '.-#'")
        shades = list('.-#')

    rotation_angles = [0, 0, 0]
    rotation_speed = [args.x_speed, args.y_speed, args.z_speed]
    zoom_level = args.zoom
    light_direction = normalize_vector((args.light_x, args.light_y, args.light_z))
    outline_char = args.outline_char

    while True:
        screen = initialize_screen(screen_width, screen_height)
        draw_cube(screen, vertices, faces, edges, screen_width, screen_height, rotation_angles, shades, zoom_level, light_direction, outline_char)
        clear_screen()
        display_screen(screen)

        for i in range(3):
            rotation_angles[i] += rotation_speed[i]
            rotation_angles[i] %= 360

        time.sleep(0.03)


