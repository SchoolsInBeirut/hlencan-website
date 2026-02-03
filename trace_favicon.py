"""
Favicon PNG to SVG tracer
Traces the white pixels from favicon.png and creates an SVG file
"""

from PIL import Image
import numpy as np

def trace_to_svg(input_path, output_path):
    # Load the image
    img = Image.open(input_path).convert('RGBA')
    width, height = img.size
    pixels = np.array(img)
    
    # Find all non-transparent white pixels
    # We'll create a binary mask where white/light pixels are 1
    alpha = pixels[:, :, 3]  # Alpha channel
    rgb = pixels[:, :, :3]   # RGB channels
    
    # Consider a pixel "on" if it has alpha > 128 and is mostly white/light
    brightness = np.mean(rgb, axis=2)
    mask = (alpha > 128) & (brightness > 128)
    
    # Find contours using a simple edge detection approach
    # We'll trace the outline of connected regions
    
    # Create SVG with path data
    svg_paths = []
    
    # Use a flood-fill approach to find connected regions
    visited = np.zeros_like(mask, dtype=bool)
    
    def trace_contour(start_y, start_x):
        """Trace the contour of a region starting from a point"""
        points = []
        
        # Find all boundary points of this connected region
        # Use BFS to find all points in this region
        from collections import deque
        queue = deque([(start_y, start_x)])
        region_points = set()
        
        while queue:
            y, x = queue.popleft()
            if y < 0 or y >= height or x < 0 or x >= width:
                continue
            if visited[y, x] or not mask[y, x]:
                continue
            
            visited[y, x] = True
            region_points.add((y, x))
            
            # Add neighbors
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width:
                    if not visited[ny, nx] and mask[ny, nx]:
                        queue.append((ny, nx))
        
        if not region_points:
            return None
        
        # Find boundary points (points with at least one non-region neighbor)
        boundary = []
        for y, x in region_points:
            is_boundary = False
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                ny, nx = y + dy, x + dx
                if ny < 0 or ny >= height or nx < 0 or nx >= width or not mask[ny, nx]:
                    is_boundary = True
                    break
            if is_boundary:
                boundary.append((x, y))  # Note: x, y for SVG coordinates
        
        return boundary
    
    # Create a simplified SVG by drawing rectangles for each pixel
    # This gives us a pixel-perfect reproduction
    rects = []
    for y in range(height):
        for x in range(width):
            if mask[y, x]:
                rects.append(f'<rect x="{x}" y="{y}" width="1" height="1"/>')
    
    # Also try to create optimized horizontal runs
    optimized_rects = []
    for y in range(height):
        x = 0
        while x < width:
            if mask[y, x]:
                # Find the run length
                run_start = x
                while x < width and mask[y, x]:
                    x += 1
                run_length = x - run_start
                optimized_rects.append(f'<rect x="{run_start}" y="{y}" width="{run_length}" height="1"/>')
            else:
                x += 1
    
    # Create the SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <g fill="white">
    {"".join(optimized_rects)}
  </g>
</svg>'''
    
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"Created SVG with {len(optimized_rects)} rectangles")
    print(f"Original size: {width}x{height}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    trace_to_svg("favicon.png", "favicon.svg")
