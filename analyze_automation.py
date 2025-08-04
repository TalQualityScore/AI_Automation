#!/usr/bin/env python3
"""
Deep analysis of the automation folder to find what's causing 37% repository size
"""

import os
import sys
from pathlib import Path

def analyze_file_content(filepath):
    """Analyze file for potential bloat sources"""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Check for base64 encoded data
        if 'base64' in content.lower() or len([line for line in content.split('\n') if len(line) > 200]) > 10:
            issues.append("Possible embedded base64 data")
            
        # Check for large string literals
        import re
        long_strings = re.findall(r'["\']([^"\']{500,})["\']', content)
        if long_strings:
            issues.append(f"Large string literals found ({len(long_strings)} strings)")
            
        # Check for large data structures
        if 'huge_data' in content or 'large_dict' in content or content.count('[') > 100:
            issues.append("Large data structures detected")
            
        # Check for repeated code patterns
        lines = content.split('\n')
        if len(lines) > 1000:
            issues.append(f"Very large file ({len(lines)} lines)")
            
        # Check for embedded images/binary data
        if any(keyword in content.lower() for keyword in ['iVBORw0KGgo', 'data:image', '/9j/', 'R0lGOD']):
            issues.append("Embedded binary/image data detected")
            
    except Exception as e:
        issues.append(f"Could not analyze: {e}")
        
    return issues

def main():
    print("🔍 Deep Analysis of Automation Folder")
    print("=" * 50)
    
    automation_path = Path("app/src/automation")
    if not automation_path.exists():
        print("❌ Automation folder not found!")
        return
    
    total_size = 0
    file_analysis = []
    
    # Analyze each file in automation folder
    for file_path in automation_path.rglob("*.py"):
        try:
            size = file_path.stat().st_size
            total_size += size
            
            # Count lines
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = len(f.readlines())
            
            # Analyze content for bloat
            issues = analyze_file_content(file_path)
            
            file_analysis.append({
                'path': file_path,
                'size': size,
                'lines': lines,
                'issues': issues
            })
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    # Sort by size
    file_analysis.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"📊 AUTOMATION FOLDER ANALYSIS")
    print(f"Total size: {total_size / 1024:.1f} KB ({total_size / 1024 / 1024:.1f} MB)")
    print(f"Total files: {len(file_analysis)}")
    print()
    
    print("🔍 LARGEST FILES:")
    print("-" * 50)
    for item in file_analysis[:15]:  # Top 15 files
        size_kb = item['size'] / 1024
        print(f"{item['path'].name:<35} {size_kb:>8.1f} KB ({item['lines']:>4} lines)")
        
        if item['issues']:
            for issue in item['issues']:
                print(f"  ⚠️  {issue}")
        
        # Flag unusually large files
        if size_kb > 50:  # Files larger than 50KB are unusual for Python
            print(f"  🚨 UNUSUALLY LARGE for Python code!")
        elif size_kb > 30:
            print(f"  ⚠️  Large file - investigate")
        print()
    
    print("🎯 SUMMARY OF ISSUES:")
    print("-" * 50)
    
    # Categorize issues
    large_files = [f for f in file_analysis if f['size'] > 50*1024]  # >50KB
    files_with_data = [f for f in file_analysis if any('data' in issue.lower() for issue in f['issues'])]
    files_with_strings = [f for f in file_analysis if any('string' in issue.lower() for issue in f['issues'])]
    
    if large_files:
        print(f"📈 {len(large_files)} files are unusually large (>50KB):")
        for f in large_files:
            print(f"   - {f['path'].name}: {f['size']/1024:.1f}KB")
    
    if files_with_data:
        print(f"💾 {len(files_with_data)} files contain embedded data:")
        for f in files_with_data:
            print(f"   - {f['path'].name}")
    
    if files_with_strings:
        print(f"📝 {len(files_with_strings)} files have large string literals:")
        for f in files_with_strings:
            print(f"   - {f['path'].name}")
    
    # Calculate what normal size should be
    avg_size_per_line = total_size / sum(f['lines'] for f in file_analysis)
    total_lines = sum(f['lines'] for f in file_analysis)
    expected_size = total_lines * 50  # ~50 bytes per line is normal
    
    print(f"\n📐 SIZE ANALYSIS:")
    print(f"Current size: {total_size/1024:.1f} KB")
    print(f"Expected size: {expected_size/1024:.1f} KB")
    print(f"Bloat factor: {total_size/expected_size:.1f}x")
    
    if total_size > expected_size * 2:
        print("🚨 SIGNIFICANT BLOAT DETECTED!")
        print("This folder is 2x+ larger than typical Python code.")

if __name__ == "__main__":
    main()