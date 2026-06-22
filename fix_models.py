# Fix script to remove duplicate indented Offer class from models.py
with open('models.py', 'r') as f:
    lines = f.readlines()

# Find and remove the indented Offer class inside CompanySettings
output = []
skip_indented_offer = False
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the indented Offer class (starts with spaces)
    if '    class Offer(Base):' in line and line.startswith('    '):
        skip_indented_offer = True
        i += 1
        continue
    
    # Skip lines that are part of the indented class
    if skip_indented_offer:
        # Keep skipping until we find a non-indented line or a line with class at column 0
        if line.strip() == '' or (line.startswith('    ') and not line.startswith('class ')):
            i += 1
            continue
        elif line.startswith('class '):
            skip_indented_offer = False
            # Don't skip this line, process it normally
        else:
            skip_indented_offer = False
    
    output.append(line)
    i += 1

# Write back
with open('models.py', 'w') as f:
    f.writelines(output)

print("Fixed models.py - removed duplicate indented Offer class")
