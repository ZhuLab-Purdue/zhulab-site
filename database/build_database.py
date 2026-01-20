import os
import glob

# 1. Setup
base_folder = "database"

# 2. Walk through every sub-folder in 'database'
# os.listdir gives us the names of the folders (e.g., 'Bi2Se3', 'WTe2')
for item in os.listdir(base_folder):
    item_path = os.path.join(base_folder, item)
    
    # We only care if it's a folder, and not a hidden folder (like .ipynb_checkpoints)
    if os.path.isdir(item_path) and not item.startswith('.'):
        material_name = item
        print(f"Processing material: {material_name}...")

        # 3. Look for data files INSIDE the folder
        # We try to find summary.txt, properties.csv, and any image
        summary_path = os.path.join(item_path, "summary.txt")
        image_files = glob.glob(os.path.join(item_path, "*.png")) + glob.glob(os.path.join(item_path, "*.jpg"))
        
        # Read the summary text (if it exists)
        summary_text = "No summary provided."
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                summary_text = f.read()

        # Handle Image (take the first one found)
        image_markdown = ""
        if image_files:
            # We need the path relative to the markdown file
            img_name = os.path.basename(image_files[0])
            image_markdown = f"![Microscopy/Structure]({img_name})"

        # 4. Generate the Page Content (index.qmd)
        # This sits INSIDE the material folder
        page_content = f"""---
title: "{material_name}"
format:
  html:
    toc: true
---

## Overview
{summary_text}

## Characterization
{image_markdown}

## Specifications
* **Data Source:** Folder `{material_name}`
* **Status:** Available for collaboration

"""
        
        # 5. Write the index.qmd file
        output_file = os.path.join(item_path, "index.qmd")
        with open(output_file, "w") as f:
            f.write(page_content)

print("Database updated! Run 'quarto preview' to see the navigation.")