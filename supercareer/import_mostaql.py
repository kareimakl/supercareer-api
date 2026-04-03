import csv
import os
import django
from datetime import datetime
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supercareer.settings')
django.setup()

from opportunities.models import FreelanceProject
from accounts.models import Skill

# Use absolute path or handle relative path better
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '..', 'web-scraping', 'data', 'mostaql_projects.csv')

def clean_budget(budget_str):
    if not budget_str:
        return None
    return budget_str.strip()

def parse_date(date_str):
    # Mostaql format: 2026-02-07 19:34:12
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None

def import_mostaql_projects():
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    print(f"Analyzing CSV: {CSV_PATH}")
    
    # Use utf-8-sig to handle Byte Order Mark (BOM) if present
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        # Read the first line to check headers manually if needed
        first_line = f.readline()
        print(f"DEBUG: First line of CSV: {repr(first_line)}")
        f.seek(0)
        
        reader = csv.DictReader(f)
        # Clean headers to remove any leading/trailing whitespace or hidden characters
        if reader.fieldnames:
            original_headers = reader.fieldnames
            reader.fieldnames = [name.strip() for name in reader.fieldnames if name]
            print(f"DEBUG: Original Headers: {original_headers}")
            print(f"DEBUG: Cleaned Headers: {reader.fieldnames}")
        else:
            print("Error: Could not read headers from CSV.")
            return
        
        count = 0
        for row in reader:
            # Map headers back to cleaned versions if necessary
            # DictReader uses cleaned headers now
            
            project_link = row.get('link')
            if not project_link:
                continue

            # Check if project already exists by source_url
            if FreelanceProject.objects.filter(source_url=project_link).exists():
                continue
            
            project_name = row.get('project_name')
            if not project_name:
                print(f"DEBUG: Skipping row missing project_name. Row keys: {list(row.keys())}")
                continue
                
            project = FreelanceProject.objects.create(
                title=project_name,
                description=row.get('project_details', ''),
                budget=clean_budget(row.get('budget')),
                duration=row.get('duration', '').strip(),
                status=row.get('project_status', 'مفتوح'),
                platform_name='Mostaql',
                source_url=project_link,
                posted_date=parse_date(row.get('publish_date'))
            )
            
            # Handle skills
            skills_str = row.get('skills')
            if skills_str:
                # Skills are comma separated and quoted
                skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                for skill_name in skills_list:
                    # Skill name might be Arabic or English
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    project.required_skills.add(skill)
            
            count += 1
            if count % 10 == 0:
                print(f"Imported {count} projects...")

    print(f"Successfully imported {count} new projects from Mostaql.")

if __name__ == '__main__':
    try:
        import_mostaql_projects()
    except Exception as e:
        print(f"CRITICAL ERROR during import: {str(e)}")
        import traceback
        traceback.print_exc()
