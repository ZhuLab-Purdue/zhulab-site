import os
import glob
import pandas as pd

# CONFIGURATION
base_folder = "database"
sidebar_file = "sidebar_config.yml"
material_links = []

# --- WIDTH SETTINGS ---
prop_table_width = "1100px"   # Fixed width for Properties
char_col1_width = "300px"    # Characterization Label
char_col2_width = "800px"    # Characterization Image
char_total_width = "1100px"  # Total Characterization

print("--- Starting Database Build ---")

# ==========================================
# PART 1: PROCESS MATERIAL DATABASE PAGES
# ==========================================
for item in os.listdir(base_folder):
    item_path = os.path.join(base_folder, item)
    
    if os.path.isdir(item_path) and not item.startswith('.'):
        material_name = item
        material_links.append(f"database/{material_name}/index.qmd")

        # --- A. SUMMARY ---
        summary_path = os.path.join(item_path, "summary.txt")
        summary_text = "_No summary provided._"
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f: summary_text = f.read()

        # --- B. PROPERTIES (Updated for Strict Fixed Width) ---
        csv_path = os.path.join(item_path, "properties.csv")
        table_html = ""
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                
                # We use !important to override styles.css rules
                # display: table !important restores the fixed layout behavior
                table_html = f'<table style="width: {prop_table_width} !important; min-width: {prop_table_width}; margin-left: auto; margin-right: auto; border-collapse: collapse; table-layout: fixed; display: table !important;">\n'
                
                # Header Row
                table_html += '  <thead>\n    <tr style="background-color: #f2f2f2; border-bottom: 2px solid #ddd;">\n'
                
                # Calculate column width (e.g., if 4 columns, each is 25%)
                num_cols = len(df.columns)
                col_width_percent = f"{100/num_cols}%" if num_cols > 0 else "auto"

                for col in df.columns:
                    table_html += f'      <th style="width: {col_width_percent}; padding: 10px; text-align: left; border: 1px solid #ddd; overflow-wrap: break-word;">{col}</th>\n'
                table_html += '    </tr>\n  </thead>\n'
                
                # Data Rows
                table_html += '  <tbody>\n'
                for index, row in df.iterrows():
                    table_html += '    <tr style="border-bottom: 1px solid #ddd;">\n'
                    for item in row:
                        table_html += f'      <td style="padding: 10px; border: 1px solid #ddd; overflow-wrap: break-word;">{item}</td>\n'
                    table_html += '    </tr>\n'
                table_html += '  </tbody>\n</table>'
            except: 
                table_html = "_Error reading properties CSV._"
        else:
            table_html = "_No properties data available._"

        # --- C. CHARACTERIZATION (Unchanged) ---
        extensions = ['*.png', '*.jpg', '*.jpeg', '*.tif', '*.tiff']
        image_files = []
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(item_path, ext)))
        image_files.sort()

        char_html = f'<table style="width: {char_total_width} !important; table-layout: fixed; border-collapse: collapse; margin-left: auto; margin-right: auto; display: table !important;">\n'
        
        for img_path in image_files:
            img_filename = os.path.basename(img_path)
            display_name = os.path.splitext(img_filename)[0].replace("_", " ").replace("-", " ")
            
            char_html += '  <tr style="border-bottom: 1px solid #ddd;">\n'
            char_html += f'    <td style="width: {char_col1_width}; text-align: center; vertical-align: middle; font-weight: bold; padding: 10px; font-size: 1.5em; overflow-wrap: break-word;">{display_name}</td>\n'
            char_html += f'    <td style="width: {char_col2_width}; padding: 10px; vertical-align: middle;"><img src="{img_filename}" style="width: 100%; height: auto; display: block;"></td>\n'
            char_html += '  </tr>\n'
        char_html += '</table>'
        if not image_files: char_html = "_No characterization images found._"

        # --- D. WRITE PAGE ---
        page_content = f"""---
title: "{material_name}"
format:
  html:
    toc: false
    page-layout: article
---

## Overview
{summary_text}

## Key Properties
{table_html}

## Characterization
{char_html}
"""
        with open(os.path.join(item_path, "index.qmd"), "w") as f:
            f.write(page_content)

# ==========================================
# PART 2 & 3: SIDEBAR CONFIG (Unchanged)
# ==========================================
root_pages = glob.glob("*.qmd")
root_links = []
for p in root_pages:
    root_links.append(f"href: {p}\n          text: ' '") 

print(f"Updating {sidebar_file}...")

with open(sidebar_file, "w") as f:
    f.write("# AUTO-GENERATED BY PYTHON. DO NOT EDIT.\n")
    f.write("website:\n")
    f.write("  sidebar:\n")
    
    # DB Sidebar
    f.write("    - id: database-sidebar\n")
    f.write("      title: 'Material Database'\n")
    f.write("      style: docked\n")
    f.write("      background: '#f8f9fa'\n")
    f.write("      contents:\n")
    f.write("        - href: database/index.qmd\n")
    f.write("          text: 'Overview'\n")
    f.write("        - section: 'Available Materials'\n")
    f.write("          contents:\n")
    for link in sorted(material_links):
        f.write(f"            - href: {link}\n")
        display_name = link.split('/')[1] 
        f.write(f"              text: '{display_name}'\n")
    
    # Global Sidebar
    f.write("\n")
    f.write("    - id: global-sidebar\n")
    f.write("      title: ' '\n")
    f.write("      style: docked\n")
    f.write("      background: '#f8f9fa'\n")
    f.write("      contents:\n")
    for link_info in root_links:
        f.write(f"        - {link_info}\n")

print("--- Build Complete! ---")