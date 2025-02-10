import math
import time
import os
import argparse
import datetime
import sys
import subprocess  # Import subprocess module

# Script metadata
AUTHOR_STRING = "Author: Arnaldo Hernandez <mailto:arjuhe@gmail.com>"
VERSION = '.001'  # Initial version - please increment manually for each modification
BUILD_STRING = f"Build: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"  # Build date and time

# ANSI color codes - Basic Colors for Fallback
COLOR_RESET = '\033[0m'
COLOR_BRIGHT_DEFAULT = '\033[91m'    # Bright Red - fallback
COLOR_NEUTRAL_DEFAULT = '\033[0m\033[92m'   # Bright Green - fallback
COLOR_DARK_DEFAULT = '\033[94m'      # Bright Blue - fallback
COLOR_OUTLINE_DEFAULT = '\033[93m'   # Bright Yellow - fallback

# Define a dictionary to map color names to ANSI codes
COLOR_MAP = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    'neutral_green_reset': '\033[0m\033[92m'  # Special case for neutral green with reset
}

CLEAR_SCREEN_CODE = '\033[2J\033[H'  # ANSI escape code to clear screen and reset cursor


def clear_screen():
    """Clears the terminal screen using ANSI escape codes."""
    print(CLEAR_SCREEN_CODE, end='')


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
    magnitude = math.sqrt(x * x + y * y + z * z)
    if magnitude == 0:
        return (0, 0, 0)
    return (x / magnitude, y / magnitude, z / magnitude)


def cross_product(vec1, vec2):
    """Calculates the cross product of two 3D vectors."""
    x1, y1, z1 = vec1
    x2, y2, z2 = vec2
    return (y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2)


def calculate_normal(face_vertices):
    """Calculates the normal vector of a face."""
    if not face_vertices or len(face_vertices) < 3:
        print("Warning: calculate_normal received invalid face_vertices:", face_vertices)
        return (0, 0, 0)
    p1, p2, p3 = face_vertices[0], face_vertices[1], face_vertices[2]
    vec1 = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    vec2 = (p3[0] - p1[0], p3[1] - p1[1], p2[2] - p1[2])
    normal = cross_product(vec1, vec2)
    return normalize_vector(normal)


def draw_line(screen, point1_2d, point2_2d, draw_char, color_code, screen_width, screen_height):
    """Draws a colored line on the screen buffer."""
    x1, y1 = point1_2d
    x2, y2 = point2_2d

    if not (0 <= x1 < screen_width and 0 <= y1 < screen_height and 0 <= x2 < screen_width and 0 <= y2 < screen_height):
        return

    if x1 == x2:  # Vertical line
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= y < screen_height:
                screen[y][x1] = (draw_char, color_code)  # Store char and color
    elif y1 == y2:  # Horizontal line
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < screen_width:
                screen[y1][x] = (draw_char, color_code)  # Store char and color
    else:  # Diagonal-ish line (very basic)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        x, y = x1, y1
        while True:
            if 0 <= x < screen_width and 0 <= y < screen_height:
                screen[y][x] = (draw_char, color_code)  # Store char and color
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy


def draw_filled_polygon(screen, points_2d, draw_char, color_code, screen_width, screen_height):
    """Draws a filled polygon with color on the screen buffer."""
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
            x_end = intersections[i + 1] if i + 1 < len(intersections) else screen_width

            for x in range(max(0, x_start), min(screen_width, x_end + 1)):
                if 0 <= y < screen_height:
                    screen[y][x] = (draw_char, color_code)  # Store char and color


def draw_cube(screen, vertices, faces, edges, screen_width, screen_height, rotation_angles, shades, zoom_level, light_direction, outline_char, bright_color_code, neutral_color_code, dark_color_code, outline_color_code, no_color):
    """Draws the filled, shaded, and outlined cube with color on the screen buffer."""

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
        if avg_z < 0:  # Back-face culling
            continue

        face_vertices_2d = [projected_vertices[v_index] for v_index in face]

        # 3-Shade gradient mapping with colors
        if no_color:  # No color mode
            draw_char = shades[1]  # Use neutral shade character, no color
            color_code = COLOR_RESET  # or empty string ''
        elif intensity > 2.0 / 3.0:  # Brightest third
            draw_char = shades[0]
            color_code = bright_color_code
        elif intensity > 1.0 / 3.0:  # Middle third
            draw_char = shades[1]
            color_code = neutral_color_code
        else:  # Darkest third
            draw_char = shades[2]
            color_code = dark_color_code

        draw_filled_polygon(screen, face_vertices_2d, draw_char, color_code, screen_width, screen_height)

    # Draw Outlines in color after filling faces
    projected_edges = []
    for edge in edges:
        v1_index, v2_index = edge
        projected_edges.append((projected_vertices[v1_index], projected_vertices[v2_index]))

    for edge_points_2d in projected_edges:
        line_color = COLOR_RESET if no_color else outline_color_code  # No outline color if no_color
        draw_line(screen, edge_points_2d[0], edge_points_2d[1], outline_char, line_color, screen_width, screen_height)


def initialize_screen(width, height):
    """Creates an empty screen buffer. Now stores (char, color_code) tuples."""
    return [[(' ', COLOR_RESET) for _ in range(width)] for _ in range(height)]


def display_screen(screen, no_color):
    """Prints the screen buffer to the terminal, including color codes."""
    for row in screen:
        colored_row = ""
        current_color = COLOR_RESET  # Start with reset color
        for char, color_code in row:
            if not no_color:  # Apply colors only if no_color is False
                if color_code != current_color:  # Change color only if needed
                    colored_row += color_code
                    current_color = color_code
            colored_row += char
        colored_row += COLOR_RESET  # Reset color at the end of each row
        print(colored_row)


def get_terminal_command():
    """Detects the terminal and returns the appropriate command to open a new window."""
    platform = sys.platform
    terminal_command = []

    if platform.startswith('linux'):
        # Prioritize gnome-terminal, xterm, konsole, fallback to xterm
        for term in ['gnome-terminal', 'konsole', 'xterm']:  # Check in order of preference
            if subprocess.run(['which', term], capture_output=True, check=False).returncode == 0:  # Check if terminal exists
                terminal_command = [term, '-e']
                return terminal_command
        return ['xterm', '-e']  # Fallback to xterm if none found

    elif platform.startswith('darwin'):  # macOS
        term_program = os.environ.get('TERM_PROGRAM')
        if term_program in ('iTerm.app', 'iTerm2'): # Prioritize iTerm if $TERM_PROGRAM indicates iTerm
            app_name = 'iTerm2' if term_program == 'iTerm2' else 'iTerm' # Consistent app name for search
            app_path_result = subprocess.run(['mdfind', f'kMDItemContentTypeTree=com.apple.application AND kMDItemDisplayName="{app_name}"'], capture_output=True, text=True, check=False)
            if app_path_result.returncode == 0 and app_path_result.stdout.strip():
                app_path = app_path_result.stdout.strip().splitlines()[0]
                return ['open', '-a', app_path]

        # Fallback to searching for iTerm2 then Terminal.app if $TERM_PROGRAM is not iTerm or iTerm not found via env var
        for app_name in ['iTerm2', 'iTerm', 'Terminal']:  # Check iTerm2 first, then generic 'Terminal'
            app_path_result = subprocess.run(['mdfind', f'kMDItemContentTypeTree=com.apple.application AND kMDItemDisplayName="{app_name}"'], capture_output=True, text=True, check=False)
            if app_path_result.returncode == 0 and app_path_result.stdout.strip():  # If mdfind finds the app
                app_path = app_path_result.stdout.strip().splitlines()[0]  # Take first result if multiple
                terminal_command = ['open', '-a', app_path]  # Use 'open -a <app path>' for macOS
                return terminal_command
        return ['open', '-a', 'Terminal']  # Fallback to default Terminal.app

    elif platform.startswith('win'):  # Windows
            return ['start', 'cmd', '/k', 'python']  # 'start cmd /k' for new cmd window

    return terminal_command  # Return empty list for unsupported platforms


def parse_arguments():
    """Parses command line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="""Rotate a 3D cube in the terminal using ASCII with color, shading, and outlines.

        This script visualizes a rotating 3D filled, shaded, and outlined cube using ASCII with ANSI colors.
        It offers 3-level shading in grayscale colors and a colored outline.
        Customize size, rotation, shading levels, outline character, perspective, light, and colors.

        Color names: black, red, green, yellow, blue, magenta, cyan, white,
                     bright_black, bright_red, bright_green, bright_yellow,
                     bright_blue, bright_magenta, bright_cyan, bright_white.
                     Use 'neutral_green_reset' for special neutral green with reset

        Example Usage:
          python cube.py -W 80 -H 40 -Z 15 -S oO@ -O '#' -XS 2.0 -YS 2.5 -ZS 1.2 -LX 1.0 -LY 0.5 -LZ -0.8
          python cube.py -W 60 -H 30 -BC bright_cyan -DC magenta -OC yellow -S '@XO'
          python cube.py --no_color -S 'X- ' # Example: No color output
          python cube.py --build_info # Display build information
          python cube.py --new_window # Run in a new terminal window
        """,
        formatter_class=argparse.RawTextHelpFormatter  # To keep formatting in help text
    )
    parser.add_argument('--width', '-W', type=int, default=60, help='Screen width (default: 60).')  # Screen dimensions
    parser.add_argument('--height', '-H', type=int, default=30, help='Screen height (default: 30).')

    # Rotation and Zoom
    parser.add_argument('--x_speed', '-XS', type=float, default=1.0, help='Rotation speed around X-axis (default: 1.0).')
    parser.add_argument('--y_speed', '-YS', type=float, default=1.5, help='Rotation speed around Y-axis (default: 1.5).')
    parser.add_argument('--z_speed', '-ZS', type=float, default=0.7, help='Rotation speed around Z-axis (default: 0.7).')
    parser.add_argument('--zoom', '-Z', type=int, default=10, help='Zoom level (perspective, default: 10). Higher values zoom in.')

    # Shading and Outline
    parser.add_argument('--shades', '-S', type=str, default='.-#', help='Shading characters (light, neutral, dark - e.g., ".-#", default: ".-#").')
    parser.add_argument('--outline_char', '-o', '-O', type=str, default='*', help='Character for cube outline (default: "*").')

    # Lighting
    parser.add_argument('--light_x', '-LX', type=float, default=1.0, help='Light X direction (default: 1.0).')
    parser.add_argument('--light_y', '-LY', type=float, default=1.0, help='Light Y direction (default: 1.0).')
    parser.add_argument('--light_z', '-LZ', type=float, default=-1.0, help='Light Z direction (default: -1.0, negative Z is towards viewer).')

    # Custom Colors
    parser.add_argument('--bright_color', '-BC', type=str, default='bright_red', help='Color for brightest shade (default: bright_red).')
    parser.add_argument('--neutral_color', '-NC', type=str, default='neutral_green_reset', help='Color for neutral shade (default: neutral_green_reset).')
    parser.add_argument('--dark_color', '-DC', type=str, default='bright_blue', help='Color for darkest shade (default: dark_blue).')
    parser.add_argument('--outline_color', '-OC', type=str, default='bright_yellow', help='Color for outline (default: bright_yellow).')

    # No Color Mode
    parser.add_argument('--no_color', '-C', action='store_true', help='Disable color output (monochrome ASCII).')

    # Build Information
    parser.add_argument('--build_info', '-BI', action='store_true', help='Display build information (date and time).')

    # New Window Mode
    parser.add_argument('--new_window', '-NW', action='store_true', help='Run the script in a new terminal window.')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.build_info:  # Print build information and exit
        print(f"{COLOR_NEUTRAL_DEFAULT}{AUTHOR_STRING}{COLOR_RESET}")  # Author
        print(f"Version: {VERSION}")  # Version
        print(f"Build Time: {BUILD_STRING}")  # Build Time
        exit()  # Exit after printing build info

    if args.new_window:  # Run in a new window
        terminal_command = get_terminal_command()  # Detect terminal

        if terminal_command:
            # Construct the command to run the script again in a new terminal window
            script_path = os.path.abspath(__file__)  # Get absolute path of the script
            command = [sys.executable, script_path]  # Start with python and script path
            for arg in sys.argv[1:]:  # Iterate through original arguments
                if arg not in ['--new_window', '-NW']:  # Exclude new_window arg itself
                    command.append(arg)  # Add other arguments

            full_command = terminal_command + command

            try:
                subprocess.Popen(full_command, start_new_session=True)
                print(f"Starting cube animation in a new terminal window using: {' '.join(terminal_command[:2])}...")  # Indicate terminal used
                exit()  # Exit original script instance
            except FileNotFoundError as e:
                print(f"Error: Terminal command not found: {terminal_command[0]}. Cannot open new window. {e}")
                print("Running in the current terminal instead.")
            except Exception as e:
                print(f"Error opening new window: {e}")
                print("Running in the current terminal instead.")
        else:
            print("No suitable terminal command found for new window. Running in the current terminal.")

    screen_width = args.width
    screen_height = args.height

    vertices = [  # Smaller cube vertices
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)
    ]

    faces = [  # Face vertex indices (counter-clockwise)
        [0, 3, 2, 1], [4, 5, 6, 7], [3, 7, 6, 2],
        [0, 1, 5, 4], [0, 4, 7, 3], [1, 2, 6, 5]
    ]

    edges = [  # Cube edges (vertex index pairs)
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    shades = list(args.shades)  # 3 shading levels
    if len(shades) != 3:
        print("Warning: Shading argument should provide exactly 3 characters. Using default '.-#'")
        shades = list('.-#')

    rotation_angles = [0, 0, 0]
    rotation_speed = [args.x_speed, args.y_speed, args.z_speed]
    zoom_level = args.zoom
    light_direction = normalize_vector((args.light_x, args.light_y, args.light_z))
    outline_char = args.outline_char
    no_color_mode = args.no_color

    # Get custom color codes, use defaults if invalid color name provided
    bright_color_code = COLOR_MAP.get(args.bright_color.lower(), COLOR_BRIGHT_DEFAULT)
    neutral_color_code = COLOR_MAP.get(args.neutral_color.lower(), COLOR_NEUTRAL_DEFAULT)
    dark_color_code = COLOR_MAP.get(args.dark_color.lower(), COLOR_DARK_DEFAULT)
    outline_color_code = COLOR_MAP.get(args.outline_color.lower(), COLOR_OUTLINE_DEFAULT)

    print(f"{COLOR_NEUTRAL_DEFAULT}{AUTHOR_STRING}{COLOR_RESET}")  # Print author in neutral color
    print(f"Version: {VERSION}")  # Print version in default color
    print(f"{BUILD_STRING}")  # Print build string
    if no_color_mode:
        print("(No color mode enabled)")
    print()  # Add an empty line for spacing

    while True:
        screen = initialize_screen(screen_width, screen_height)
        draw_cube(screen, vertices, faces, edges, screen_width, screen_height, rotation_angles, shades, zoom_level, light_direction, outline_char, bright_color_code, neutral_color_code, dark_color_code, outline_color_code, no_color_mode)
        clear_screen()
        display_screen(screen, no_color_mode)

        for i in range(3):
            rotation_angles[i] += rotation_speed[i]
            rotation_angles[i] %= 360

        time.sleep(0.03)
