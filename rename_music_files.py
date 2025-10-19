import os
import glob

def rename_music_files():
    audio_dir = "data/audio_samples"
    
    # Check if directory exists
    if not os.path.exists(audio_dir):
        print(f"Error: Directory '{audio_dir}' does not exist!")
        return
    
    # Get all audio files in the directory
    audio_files = glob.glob(os.path.join(audio_dir, "*.*"))
    
    if not audio_files:
        print(f"No files found in '{audio_dir}'")
        return
    
    print(f"Found {len(audio_files)} files in '{audio_dir}'")
    renamed_count = 0
    
    for old_path in audio_files:
        # Get the filename without directory path
        old_filename = os.path.basename(old_path)
        
        # Replace spaces with underscores
        new_filename = old_filename.replace(" ", "_")
        
        # Only rename if the filename actually contains spaces
        if old_filename != new_filename:
            new_path = os.path.join(audio_dir, new_filename)
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_filename}' -> '{new_filename}'")
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming '{old_filename}': {str(e)}")
    
    print(f"\nRenaming completed! {renamed_count} files were renamed.")

# More advanced version with additional cleaning options
def advanced_rename_music_files():
    audio_dir = "data/audio_samples"
    
    if not os.path.exists(audio_dir):
        print(f"Error: Directory '{audio_dir}' does not exist!")
        return
    
    audio_files = glob.glob(os.path.join(audio_dir, "*.*"))
    
    if not audio_files:
        print(f"No files found in '{audio_dir}'")
        return
    
    print(f"Found {len(audio_files)} files in '{audio_dir}'")
    renamed_count = 0
    
    for old_path in audio_files:
        old_filename = os.path.basename(old_path)
        new_filename = old_filename
        
        # Apply multiple cleaning rules
        new_filename = new_filename.replace(" ", "_")  # Spaces to underscores
        new_filename = new_filename.replace("(", "")   # Remove parentheses
        new_filename = new_filename.replace(")", "")   # Remove parentheses
        new_filename = new_filename.replace("[", "")   # Remove brackets
        new_filename = new_filename.replace("]", "")   # Remove brackets
        new_filename = new_filename.replace("'", "")   # Remove single quotes
        new_filename = new_filename.replace('"', "")   # Remove double quotes
        
        # Only rename if the filename actually changed
        if old_filename != new_filename:
            new_path = os.path.join(audio_dir, new_filename)
            
            # Check if target file already exists
            if os.path.exists(new_path):
                print(f"Warning: '{new_filename}' already exists. Skipping '{old_filename}'")
                continue
            
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_filename}' -> '{new_filename}'")
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming '{old_filename}': {str(e)}")
    
    print(f"\nAdvanced renaming completed! {renamed_count} files were renamed.")

# Simple version that just shows what would be renamed (dry run)
def dry_run_rename():
    audio_dir = "data/audio_samples"
    
    if not os.path.exists(audio_dir):
        print(f"Error: Directory '{audio_dir}' does not exist!")
        return
    
    audio_files = glob.glob(os.path.join(audio_dir, "*.*"))
    
    if not audio_files:
        print(f"No files found in '{audio_dir}'")
        return
    
    print(f"DRY RUN - Found {len(audio_files)} files in '{audio_dir}':")
    files_with_spaces = 0
    
    for old_path in audio_files:
        old_filename = os.path.basename(old_path)
        new_filename = old_filename.replace(" ", "_")
        
        if old_filename != new_filename:
            print(f"Would rename: '{old_filename}' -> '{new_filename}'")
            files_with_spaces += 1
        else:
            print(f"No change needed: '{old_filename}'")
    
    print(f"\nDry run completed. {files_with_spaces} files would be renamed.")

if __name__ == "__main__":
    print("Choose renaming option:")
    print("1. Basic rename (spaces to underscores)")
    print("2. Advanced rename (spaces + remove special characters)")
    print("3. Dry run (show what would be renamed)")
    
    choice = input("Enter your choice (1/2/3): ").strip()
    
    if choice == "1":
        rename_music_files()
    elif choice == "2":
        advanced_rename_music_files()
    elif choice == "3":
        dry_run_rename()
    else:
        print("Invalid choice. Running basic rename...")
        rename_music_files()