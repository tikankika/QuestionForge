#!/usr/bin/env python3
"""
Setup MQG Folders Configuration

Interactive tool for managing MQG folder locations in config/mqg_folders.json.
This makes it easy to add, edit, or remove frequently used MQG folders.

Usage:
    python scripts/setup_mqg_folders.py

Example:
    python scripts/setup_mqg_folders.py
    # Interactive menu to add/edit/remove folders
"""

import sys
import json
from pathlib import Path


def load_config():
    """Load mqg_folders.json config"""
    project_root = Path(__file__).parent.parent
    config_file = project_root / "config" / "mqg_folders.json"

    if not config_file.exists():
        return {"folders": [], "default_output_dir": "output", "remember_last_selection": True}

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config):
    """Save config to mqg_folders.json"""
    project_root = Path(__file__).parent.parent
    config_file = project_root / "config" / "mqg_folders.json"

    # Create config directory if it doesn't exist
    config_file.parent.mkdir(exist_ok=True)

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def expand_path(path_str):
    """Expand ~ and resolve path"""
    return Path(path_str).expanduser().resolve()


def display_folders(config):
    """Display current folders"""
    print("\n" + "=" * 70)
    print("NUVARANDE MQG FOLDERS")
    print("=" * 70)

    if not config['folders']:
        print("Inga folders konfigurerade ännu.")
        return

    for i, folder in enumerate(config['folders'], 1):
        print(f"\n{i}. {folder['name']}")
        print(f"   Path: {folder['path']}")
        print(f"   Språk: {folder.get('default_language', 'en')}")
        if 'description' in folder:
            print(f"   Info: {folder['description']}")

        # Check if path exists
        expanded_path = expand_path(folder['path'])
        if expanded_path.exists():
            print(f"   Status: ✓ Folder finns")
        else:
            print(f"   Status: ✗ Folder finns inte")


def add_folder(config):
    """Add new folder to config"""
    print("\n" + "=" * 70)
    print("LÄGG TILL NY MQG FOLDER")
    print("=" * 70)

    # Get folder name
    name = input("\nNamn (t.ex. 'Biologi BIOG001X'): ").strip()
    if not name:
        print("Avbruten - inget namn angivet")
        return

    # Get path
    path = input("Path (t.ex. '~/Nextcloud/Courses/...'): ").strip()
    if not path:
        print("Avbruten - ingen path angiven")
        return

    # Verify path exists
    expanded_path = expand_path(path)
    if not expanded_path.exists():
        confirm = input(f"\n⚠️  Varning: Path finns inte: {expanded_path}\nLägg till ändå? (j/n): ")
        if confirm.lower() != 'j':
            print("Avbruten")
            return

    # Get language
    language = input("Default språk [sv]: ").strip() or "sv"

    # Get description (optional)
    description = input("Beskrivning (optional): ").strip()

    # Create folder entry
    folder_entry = {
        "name": name,
        "path": path,
        "default_language": language
    }

    if description:
        folder_entry["description"] = description

    # Add to config
    config['folders'].append(folder_entry)
    save_config(config)

    print(f"\n✓ Folder '{name}' tillagd!")


def edit_folder(config):
    """Edit existing folder"""
    if not config['folders']:
        print("\nInga folders att redigera.")
        return

    display_folders(config)

    try:
        choice = input("\nRedigera folder (nummer): ").strip()
        idx = int(choice) - 1

        if idx < 0 or idx >= len(config['folders']):
            print("Ogiltigt nummer")
            return

        folder = config['folders'][idx]

        print(f"\nRedigerar: {folder['name']}")
        print("(Tryck ENTER för att behålla nuvarande värde)")

        # Edit name
        new_name = input(f"Namn [{folder['name']}]: ").strip()
        if new_name:
            folder['name'] = new_name

        # Edit path
        new_path = input(f"Path [{folder['path']}]: ").strip()
        if new_path:
            folder['path'] = new_path

        # Edit language
        new_lang = input(f"Språk [{folder.get('default_language', 'en')}]: ").strip()
        if new_lang:
            folder['default_language'] = new_lang

        # Edit description
        current_desc = folder.get('description', '')
        new_desc = input(f"Beskrivning [{current_desc}]: ").strip()
        if new_desc:
            folder['description'] = new_desc
        elif new_desc == '' and 'description' in folder:
            del folder['description']

        save_config(config)
        print(f"\n✓ Folder uppdaterad!")

    except (ValueError, IndexError):
        print("Ogiltigt val")


def remove_folder(config):
    """Remove folder from config"""
    if not config['folders']:
        print("\nInga folders att ta bort.")
        return

    display_folders(config)

    try:
        choice = input("\nTa bort folder (nummer): ").strip()
        idx = int(choice) - 1

        if idx < 0 or idx >= len(config['folders']):
            print("Ogiltigt nummer")
            return

        folder = config['folders'][idx]
        confirm = input(f"\nSäker på att ta bort '{folder['name']}'? (j/n): ")

        if confirm.lower() == 'j':
            config['folders'].pop(idx)
            save_config(config)
            print(f"\n✓ Folder borttagen!")
        else:
            print("Avbruten")

    except (ValueError, IndexError):
        print("Ogiltigt val")


def main_menu():
    """Main menu loop"""
    config = load_config()

    while True:
        display_folders(config)

        print("\n" + "=" * 70)
        print("ALTERNATIV")
        print("=" * 70)
        print("  a) Lägg till ny folder")
        print("  e) Redigera existerande folder")
        print("  d) Ta bort folder")
        print("  q) Avsluta")

        choice = input("\nVälj (a/e/d/q): ").strip().lower()

        if choice == 'a':
            add_folder(config)
        elif choice == 'e':
            edit_folder(config)
        elif choice == 'd':
            remove_folder(config)
        elif choice == 'q':
            print("\nAvslutar...")
            break
        else:
            print("\nOgiltigt val. Försök igen.")

        # Reload config after changes
        config = load_config()

    print("\nKonfiguration sparad i: config/mqg_folders.json")
    print()


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nAvbrutet av användare")
        sys.exit(0)
