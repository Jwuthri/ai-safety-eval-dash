#!/usr/bin/env python3
"""
Script to fix datetime serialization in all Pydantic models.

Updates all models with datetime fields to use proper ConfigDict with json_encoders.
"""

import os
import re
from pathlib import Path


def fix_model_file(file_path: Path):
    """Fix datetime serialization in a single model file."""
    content = file_path.read_text()
    
    # Skip if already has ConfigDict import
    if 'from pydantic import BaseModel, ConfigDict' in content:
        print(f"✅ {file_path.name} - Already has ConfigDict import")
        return False
    
    # Skip if no datetime fields
    if ': datetime' not in content:
        return False
    
    print(f"🔧 Fixing {file_path.name}...")
    
    # Add ConfigDict import
    content = content.replace(
        'from pydantic import BaseModel, Field',
        'from pydantic import BaseModel, ConfigDict, Field'
    )
    
    # Replace old Config class with model_config for classes with datetime and from_attributes
    pattern = r'(class \w+\(BaseModel\):.*?)(    class Config:\s+from_attributes = True)'
    
    def replace_config(match):
        class_def = match.group(1)
        if ': datetime' in class_def:
            return class_def + '    model_config = ConfigDict(\n        from_attributes=True,\n        json_encoders={datetime: lambda v: v.isoformat() if v else None}\n    )'
        return match.group(0)
    
    content = re.sub(pattern, replace_config, content, flags=re.DOTALL)
    
    file_path.write_text(content)
    return True


def main():
    """Fix all model files."""
    models_dir = Path(__file__).parent.parent / 'app' / 'models'
    
    print(f"\n{'='*70}")
    print("🔧 Fixing DateTime Serialization in Pydantic Models")
    print(f"{'='*70}\n")
    
    fixed_count = 0
    
    for model_file in models_dir.glob('*.py'):
        if model_file.name.startswith('__'):
            continue
        
        if fix_model_file(model_file):
            fixed_count += 1
    
    print(f"\n{'='*70}")
    print(f"✨ Fixed {fixed_count} model files!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()

