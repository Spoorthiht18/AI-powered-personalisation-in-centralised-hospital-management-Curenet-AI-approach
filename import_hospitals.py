#!/usr/bin/env python
"""
Simple script to test CSV hospital import
Run this from the project root directory
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curenet_ai.settings')
django.setup()

from django.core.management import call_command

def main():
    print("🏥 CureNet AI - Hospital CSV Import Tool")
    print("=" * 50)
    
    # Check if CSV file exists
    csv_file = 'hospital_directory.csv'
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        print("Please ensure the hospital_directory.csv file is in the project root directory")
        return
    
    print(f"✅ Found CSV file: {csv_file}")
    
    # First, do a dry run to see what would be imported
    print("\n🔍 Performing dry run to preview import...")
    try:
        call_command('import_csv_hospitals', csv_file=csv_file, dry_run=True)
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return
    
    # Ask user if they want to proceed
    print("\n" + "=" * 50)
    response = input("Do you want to proceed with the actual import? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        print("\n🚀 Starting actual import...")
        try:
            call_command('import_csv_hospitals', csv_file=csv_file)
            print("\n✅ Import completed successfully!")
            print("\nYou can now:")
            print("1. Visit /hospitals/ to see all imported hospitals")
            print("2. Use the search functionality to find specific hospitals")
            print("3. Check the admin panel to manage hospital data")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    else:
        print("\n⏭️ Import cancelled. No data was imported.")
        print("You can run this script again later when you're ready.")

if __name__ == '__main__':
    main()
