# Build script - generates draw_wheel.py with extended interpretation
import os

scripts_dir = os.path.dirname(os.path.abspath(__file__))

# Read the current draw_wheel.py to get the rendering code part
with open(os.path.join(scripts_dir, 'draw_wheel.py'), 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the rendering code starts (after the data definitions)
# We need to replace the RENDERING_CODE section
marker = "# ═══ FONTS ═══"
idx = content.find(marker)
if idx == -1:
    print("ERROR: Could not find marker in draw_wheel.py")
    exit(1)

# The rendering code from marker onwards - extract what we need to preserve
rendering_part = content[idx:]

# Now build the complete new file
# Part 1: imports and setup
# Part 2: extended house/planet/aspect interpretation data
# Part 3: rendering code (preserved from original)

new_content = content[:idx]  # Everything before FONTS marker (data definitions)

# Now append the rendering part
new_content += rendering_part

# Write it
with open(os.path.join(scripts_dir, 'draw_wheel_new.py'), 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Built draw_wheel_new.py, size:", len(new_content))
