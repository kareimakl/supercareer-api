import os
import django
import sys
import csv
from datetime import datetime

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supercareer.settings')
django.setup()

from opportunities.models import FreelanceProject
from accounts.models import Skill

def parse_date(date_str):
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError) as e:
        print(f"Date parse error: {e}")
        return None

def import_data(csv_path):
    count = 0
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return 0
        
    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        headers = [h.strip() for h in reader.fieldnames] if reader.fieldnames else []
        reader.fieldnames = headers
        print(f"Headers: {headers}")

        for row in reader:
            link = row.get('link')
            if not link:
                print("Skipping row: no link")
                continue
            
            if FreelanceProject.objects.filter(source_url=link).exists():
                print(f"Link exists: {link[:50]}...")
                continue
            
            try:
                project = FreelanceProject.objects.create(
                    title=row.get('project_name', ''),
                    description=row.get('project_details', ''),
                    budget=row.get('budget', '').strip() if row.get('budget') else None,
                    duration=row.get('duration', '').strip() if row.get('duration') else None,
                    status=row.get('project_status', 'مفتوح'),
                    platform_name='Mostaql',
                    source_url=link,
                    posted_date=parse_date(row.get('publish_date'))
                )
                
                # Skills
                skills_str = row.get('skills')
                if skills_str:
                    skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                    for skill_name in skills_list:
                        skill, _ = Skill.objects.get_or_create(name=skill_name)
                        project.required_skills.add(skill)
                
                count += 1
                print(f"Imported: {project.title[:50]}...")
            except Exception as e:
                print(f"Error importing row: {e}")
                import traceback
                traceback.print_exc()
    return count

if __name__ == "__main__":
    csv_path = os.path.join('..', 'web-scraping', 'data', 'mostaql_projects.csv')
    print(f"Testing import from: {csv_path}")
    count = import_data(csv_path)
    print(f"Total imported: {count}")
