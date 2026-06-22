#!/usr/bin/env python3
"""
Setup script for Phase 1 integration
Automatically updates main.py to include Phase 1 routers
"""

import re
from pathlib import Path

def update_main_py():
    """Update main.py to include Phase 1 routers."""
    main_py_path = Path("main.py")
    
    if not main_py_path.exists():
        print("❌ main.py not found")
        return False
    
    content = main_py_path.read_text()
    
    # Update imports
    import_line = "from routers import employees, leave, timesheet, appraisal, documents, notifications, upload, recruitment, finance, requisition"
    if import_line in content and "leave_management" not in content:
        new_import_line = import_line + "\nfrom routers import hr_tools, ats, calendar_integration, assessments, reporting, document_generation\nfrom routers import leave_management, employee_documents"
        old_import = import_line + "\nfrom routers import hr_tools, ats, calendar_integration, assessments, reporting, document_generation"
        content = content.replace(old_import, new_import_line)
        print("✓ Updated router imports")
    
    # Add router registration
    if "app.include_router(document_generation.router)" in content and "leave_management.router" not in content:
        insert_line = "app.include_router(document_generation.router)"
        replacement = insert_line + "\napp.include_router(leave_management.router)\napp.include_router(employee_documents.router)"
        content = content.replace(insert_line, replacement)
        print("✓ Registered Phase 1 routers")
    
    main_py_path.write_text(content)
    return True

def run_seed():
    """Run the Phase 1 seed script."""
    import subprocess
    print("\n📊 Running Phase 1 seed script...")
    result = subprocess.run(["python", "seed_phase1.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    print("=" * 50)
    print("Phase 1 Integration Setup")
    print("=" * 50)
    
    if update_main_py():
        print("\n✓ main.py updated successfully")
        print("\n📌 Next steps:")
        print("  1. Restart backend server")
        print("  2. Run seed script: python seed_phase1.py")
        print("  3. Test endpoints with:")
        print("     - GET /leave/types")
        print("     - GET /employees/1/file-summary")
    else:
        print("\n❌ Failed to update main.py")
