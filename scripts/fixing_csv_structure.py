"""
Script to fix ArianaGrande.csv structure to match other artist CSV files
Converts from: Artist,Title,Album,Date,Lyric,Year
To: ,Artist,Title,Album,Year,Date,Lyric (with index column)
"""
import pandas as pd
from pathlib import Path
import sys

def fix_ariana_grande_csv():
    """Fix the ArianaGrande.csv file structure"""
    
    # Define paths
    csv_path = Path("data/raw/csv/ArianaGrande.csv")
    backup_path = Path("data/raw/csv/ArianaGrande_backup.csv")
    
    print("="*60)
    print("Fixing ArianaGrande.csv Structure")
    print("="*60 + "\n")
    
    # Check if file exists
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        print("\n💡 Make sure the file exists at:")
        print(f"   {csv_path.absolute()}")
        return 1
    
    try:
        # Read the CSV file
        print(f"📂 Reading: {csv_path.name}")
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        print(f"   Original shape: {df.shape}")
        print(f"   Original columns: {list(df.columns)}")
        
        # Check current structure
        expected_old_cols = ['Artist', 'Title', 'Album', 'Date', 'Lyric', 'Year']
        
        if list(df.columns) == expected_old_cols:
            print("\n✅ Detected old format (Artist,Title,Album,Date,Lyric,Year)")
            
            # Reorder columns to match the standard format
            # Standard: ,Artist,Title,Album,Year,Date,Lyric
            df = df[['Artist', 'Title', 'Album', 'Year', 'Date', 'Lyric']]
            
            print("   Reordered to: Artist,Title,Album,Year,Date,Lyric")
            
        elif list(df.columns)[1:] == expected_old_cols:
            # Already has unnamed index column
            print("\n⚠️  File already has index column, reordering...")
            df = df[['Artist', 'Title', 'Album', 'Year', 'Date', 'Lyric']]
            
        else:
            print("\n⚠️  Unexpected column structure:")
            print(f"   Found: {list(df.columns)}")
            
            # Try to map columns intelligently
            col_mapping = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'artist' in col_lower:
                    col_mapping[col] = 'Artist'
                elif 'title' in col_lower:
                    col_mapping[col] = 'Title'
                elif 'album' in col_lower:
                    col_mapping[col] = 'Album'
                elif 'year' in col_lower:
                    col_mapping[col] = 'Year'
                elif 'date' in col_lower:
                    col_mapping[col] = 'Date'
                elif 'lyric' in col_lower:
                    col_mapping[col] = 'Lyric'
            
            if len(col_mapping) == 6:
                df = df.rename(columns=col_mapping)
                df = df[['Artist', 'Title', 'Album', 'Year', 'Date', 'Lyric']]
                print("   ✅ Mapped and reordered columns")
            else:
                print("   ❌ Could not map all columns automatically")
                return 1
        
        # Create backup
        print(f"\n💾 Creating backup: {backup_path.name}")
        original_df = pd.read_csv(csv_path, encoding='utf-8')
        original_df.to_csv(backup_path, index=False, encoding='utf-8')
        
        # Save fixed file
        print(f"💾 Saving fixed file: {csv_path.name}")
        # Save with index=True to create the unnamed index column like other files
        df.to_csv(csv_path, index=True, encoding='utf-8')
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        df_verify = pd.read_csv(csv_path, encoding='utf-8')
        print(f"   New shape: {df_verify.shape}")
        print(f"   New columns: {list(df_verify.columns)}")
        
        # Check if it matches the expected format
        expected_cols = ['Unnamed: 0', 'Artist', 'Title', 'Album', 'Year', 'Date', 'Lyric']
        if list(df_verify.columns) == expected_cols:
            print("\n✅ SUCCESS! File structure now matches other CSV files")
            print(f"   Format: {', '.join(expected_cols)}")
        else:
            print("\n⚠️  Structure updated but may need manual review")
            print(f"   Expected: {expected_cols}")
            print(f"   Got: {list(df_verify.columns)}")
        
        # Show sample
        print("\n📊 First row sample:")
        print(df_verify.head(1).to_string())
        
        # Statistics
        print(f"\n📈 Statistics:")
        print(f"   Total songs: {len(df)}")
        print(f"   Artist(s): {df['Artist'].nunique()}")
        print(f"   Unique titles: {df['Title'].nunique()}")
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['Artist', 'Title'], keep=False)
        if duplicates.any():
            print(f"   ⚠️  Found {duplicates.sum()} duplicate songs (same artist+title)")
        
        print("\n" + "="*60)
        print("✅ ArianaGrande.csv has been fixed!")
        print("="*60)
        
        print("\n📝 Next steps:")
        print("   1. Run: python setup_database.py")
        print("   2. Test: python main.py <audio_file>")
        print(f"\n💡 Backup saved at: {backup_path}")
        print("   (You can delete it once you verify everything works)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def check_all_csv_structures():
    """Check and report structure of all CSV files in the directory"""
    csv_dir = Path("data/raw/csv")
    
    print("\n" + "="*60)
    print("Checking All CSV File Structures")
    print("="*60 + "\n")
    
    if not csv_dir.exists():
        print(f"❌ Directory not found: {csv_dir}")
        return
    
    csv_files = list(csv_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in: {csv_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV file(s)\n")
    
    structures = {}
    
    for csv_file in sorted(csv_files):
        try:
            df = pd.read_csv(csv_file, nrows=0)  # Just read headers
            col_tuple = tuple(df.columns)
            
            if col_tuple not in structures:
                structures[col_tuple] = []
            structures[col_tuple].append(csv_file.name)
            
        except Exception as e:
            print(f"⚠️  Error reading {csv_file.name}: {e}")
    
    # Display results
    print("📊 Structure Summary:")
    print("-"*60)
    
    for i, (cols, files) in enumerate(structures.items(), 1):
        print(f"\nStructure #{i} ({len(files)} file(s)):")
        print(f"   Columns: {', '.join(cols)}")
        print(f"   Files:")
        for f in files[:5]:  # Show first 5
            print(f"      • {f}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more")
    
    # Highlight inconsistencies
    if len(structures) > 1:
        print("\n⚠️  INCONSISTENT STRUCTURES DETECTED!")
        print("   All CSV files should have the same structure")
        print("   Run this script to fix ArianaGrande.csv")
    else:
        print("\n✅ All CSV files have consistent structure!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix ArianaGrande.csv structure to match other artist files"
    )
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Check structure of all CSV files'
    )
    
    args = parser.parse_args()
    
    if args.check_all:
        check_all_csv_structures()
    else:
        sys.exit(fix_ariana_grande_csv())