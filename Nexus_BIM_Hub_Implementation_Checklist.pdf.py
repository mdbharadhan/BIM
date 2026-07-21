from fpdf import FPDF

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Header Title
pdf.set_font("Helvetica", "B", 18)
pdf.set_text_color(15, 23, 42)
pdf.cell(0, 10, "Nexus BIM Hub - Project Implementation Checklist", ln=True, align="C")

pdf.set_font("Helvetica", "I", 10)
pdf.set_text_color(100, 116, 139)
pdf.cell(0, 8, "Complete Architectural System Verification Checklist", ln=True, align="C")
pdf.ln(8)

# Checklist Sections
sections = {
    "1. Core Root Configuration": [
        "app.py - Entry point, state initialization, navigation routing",
        "database.py & config.py - SQLite schema definition & global paths",
        "requirements.txt, README.md, .gitignore - Environment configurations"
    ],
    "2. UI Shell & Shared Components": [
        "login.py - Authentication gate & session handler",
        "navbar.py & sidebar.py - Header identity & sidebar navigation",
        "footer.py - Standard enterprise system footer",
        "cards.py, charts.py, statistics.py - KPI cards and Plotly chart renderers",
        "upload.py, tables.py, search.py, filters.py - Reusable data components",
        "activity.py, notifications.py, export.py - Audit logs & alerts"
    ],
    "3. Core Business Logic Modules": [
        "users.py, buildings.py, floors.py, rooms.py - Asset CRUD modules",
        "bim_models.py, structural.py, equipment.py - Engineering domain models",
        "inspections.py, maintenance.py, analytics.py - Operations telemetry",
        "permissions.py - Role-Based Access Control (RBAC) guard logic"
    ],
    "4. Multi-Page Applications": [
        "Dashboard.py, Buildings.py, Floors.py, Rooms.py",
        "BIM_Models.py, Structural.py, Reports.py, Analytics.py",
        "AI_Assistant.py, Notifications.py, Settings.py, Profile.py"
    ],
    "5. Database & Integration Tests": [
        "database/init_db.py - DB schema & sample seed data",
        "database/queries.py - Helper SQL execution wrappers",
        "tests/ (test_login, test_database, test_dashboard, test_reports)"
    ]
}

# Render Sections & Checkboxes
for section_title, items in sections.items():
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(0, 8, f"  {section_title}", ln=True, fill=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)
    for item in items:
        pdf.cell(10)  # Left indent
        
        # Draw Checkbox Box
        curr_x, curr_y = pdf.get_x(), pdf.get_y()
        pdf.rect(curr_x, curr_y + 1.5, 3.5, 3.5)
        
        # Draw Checkmark
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(34, 197, 94)
        pdf.text(curr_x + 0.6, curr_y + 4.2, "X")
        
        # Reset Font & Text
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(6)  # Space after checkbox
        
        pdf.multi_cell(0, 6, item)
    pdf.ln(3)

# Save to PDF file
pdf.output("Nexus_BIM_Hub_Implementation_Checklist.pdf")
print("PDF created successfully!")