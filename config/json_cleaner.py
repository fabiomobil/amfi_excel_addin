#!/usr/bin/env python3
"""
JSON Cleaner - Removes comments from JSON files to make them valid JSON
"""

import json
import glob
import re
import os
from typing import List

def clean_json_comments(content: str) -> str:
    """
    Remove JSON comments while preserving structure.
    Handles both line comments (//) and comment-like entries with empty values.
    """
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        original_line = line
        
        # Skip lines that are just comments
        stripped = line.strip()
        if (stripped.startswith('//') or 
            stripped.startswith('"//') or
            stripped == ''):
            continue
        
        # Handle comment entries with empty values like: "// comment": "",
        if re.match(r'^\s*"//[^"]*":\s*"",?\s*$', line):
            continue
            
        # Remove inline comments - be careful about strings
        if '//' in line:
            # Simple heuristic: if we see //, assume it's a comment
            # This could be improved to handle // inside strings properly
            in_string = False
            escape_next = False
            comment_start = -1
            
            for i, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string and char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    comment_start = i
                    break
            
            if comment_start != -1:
                line = line[:comment_start].rstrip()
                if not line.strip():
                    continue
        
        # Add the line if it has content
        if line.strip():
            cleaned_lines.append(line)
    
    # Join and fix trailing commas
    content = '\n'.join(cleaned_lines)
    
    # Remove trailing commas before closing brackets/braces
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    return content

def clean_file(file_path: str) -> bool:
    """Clean a single JSON file"""
    try:
        print(f"Processing: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Clean comments
        cleaned_content = clean_json_comments(original_content)
        
        # Validate JSON
        try:
            data = json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Still invalid JSON after cleaning: {e}")
            return False
        
        # Write back with proper formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  SUCCESS: Cleaned and validated")
        return True
        
    except Exception as e:
        print(f"  ERROR: Failed to process: {e}")
        return False

def main():
    config_dir = '/mnt/c/amfi/config'
    
    # Get all JSON files except global_constants.json
    json_files = glob.glob(os.path.join(config_dir, '**/*.json'), recursive=True)
    global_constants_file = os.path.join(config_dir, 'global_constants.json')
    json_files = [f for f in json_files if f != global_constants_file]
    
    print(f"Found {len(json_files)} JSON files to clean")
    
    success_count = 0
    failed_files = []
    
    for file_path in json_files:
        if clean_file(file_path):
            success_count += 1
        else:
            failed_files.append(file_path)
    
    print(f"\\n=== RESULTS ===")
    print(f"Successfully cleaned: {success_count}/{len(json_files)}")
    
    if failed_files:
        print(f"Failed files:")
        for file_path in failed_files:
            print(f"  - {file_path}")
    
    return len(failed_files)

if __name__ == '__main__':
    exit(main())