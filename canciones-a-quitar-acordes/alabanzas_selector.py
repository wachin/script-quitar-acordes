import os
import curses
import glob

def parse_song_file(file_path):
    """Parse a song file and return title, artist and lyrics sections"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
    except:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read().splitlines()
    
    # Extract title and artist (first two non-empty lines)
    title = ""
    artist = ""
    lyrics_start = 0
    
    for i, line in enumerate(content):
        if line.strip() and not line.startswith('//'):
            if not title:
                title = line.strip()
            elif not artist:
                artist = line.strip()
                lyrics_start = i + 1
                break
    
    # Parse lyrics sections
    sections = []
    current_section = {"title": "", "content": []}
    
    for line in content[lyrics_start:]:
        if line.startswith('//'):
            # If we have a previous section, save it
            if current_section["title"] or current_section["content"]:
                sections.append(current_section)
            
            # Start new section
            section_title = line[2:].strip()
            current_section = {"title": section_title, "content": []}
        elif line.strip():
            current_section["content"].append(line)
    
    # Add the last section
    if current_section["title"] or current_section["content"]:
        sections.append(current_section)
    
    return title, artist, sections

def convert_to_markdown(title, artist, sections):
    """Convert song data to markdown format"""
    markdown = f"## {title}\n"
    markdown += f"### {artist}\n\n"
    
    for section in sections:
        if section["title"]:
            markdown += f"**{section['title']}**\n"
        if section["content"]:
            markdown += "\n".join(section["content"]) + "\n\n"
    
    return markdown

def safe_addstr(stdscr, y, x, text, max_width=None):
    """Safely add string to screen, handling edge cases"""
    try:
        height, width = stdscr.getmaxyx()
        if max_width is None:
            max_width = width - x - 1
        
        if y < height and x < width:
            # Truncate text if it's too long
            if len(text) > max_width:
                text = text[:max_width-3] + "..."
            stdscr.addstr(y, x, text)
        return True
    except:
        return False

def select_files(stdscr, files):
    """Allow user to select and order files using ncurses"""
    curses.curs_set(0)
    stdscr.clear()
    
    selected = []
    available = files.copy()
    current_index = 0
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Check if screen is too small
        if height < 10 or width < 40:
            stdscr.addstr(0, 0, "Pantalla demasiado pequeña")
            stdscr.addstr(1, 0, "Redimensiona la terminal o usa")
            stdscr.addstr(2, 0, "una pantalla más grande")
            stdscr.refresh()
            curses.napms(2000)
            return None
        
        # Display title
        title = "Selecciona el orden de las alabanzas"
        subtitle = "ENTER: seleccionar, q: salir, s: guardar"
        
        safe_addstr(stdscr, 0, max(0, (width - len(title)) // 2), title)
        safe_addstr(stdscr, 1, max(0, (width - len(subtitle)) // 2), subtitle)
        
        # Display available files
        safe_addstr(stdscr, 3, 2, "Archivos disponibles:")
        for i, file in enumerate(available):
            if i >= height - 10:  # Don't go beyond screen
                break
                
            prefix = "-> " if i == current_index else "   "
            display_text = f"{prefix}{os.path.basename(file)}"
            safe_addstr(stdscr, 5 + i, 2, display_text, width // 2 - 3)
        
        # Display selected files
        safe_addstr(stdscr, 3, width // 2, "Orden seleccionado:")
        for i, file in enumerate(selected):
            if i >= height - 10:  # Don't go beyond screen
                safe_addstr(stdscr, 5 + i, width // 2, "... más archivos ...")
                break
                
            display_text = f"{i+1}. {os.path.basename(file)}"
            safe_addstr(stdscr, 5 + i, width // 2, display_text, width // 2 - 2)
        
        # Get user input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(available) - 1:
            current_index += 1
        elif key == 10:  # Enter key
            if available:
                selected.append(available.pop(current_index))
                if current_index >= len(available) and available:
                    current_index = len(available) - 1
        elif key == ord('q') or key == ord('Q'):
            return None
        elif key == ord('s') or key == ord('S'):
            return selected
    
    return selected

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)
    stdscr.clear()
    
    # Find all text files in current directory
    files = glob.glob("*.txt")
    
    if not files:
        safe_addstr(stdscr, 0, 0, "No se encontraron archivos .txt en el directorio actual")
        stdscr.getch()
        return
    
    # Let user select and order files
    selected_files = select_files(stdscr, files)
    
    if not selected_files:
        return
    
    # Convert each file to markdown and combine
    combined_markdown = ""
    for file_path in selected_files:
        title, artist, sections = parse_song_file(file_path)
        combined_markdown += convert_to_markdown(title, artist, sections)
        combined_markdown += "\n---\n\n"  # Separator between songs
    
    # Save to file
    output_file = "alabanzas_combinadas.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_markdown)
    
    # Show success message
    stdscr.clear()
    safe_addstr(stdscr, 0, 0, f"Archivo '{output_file}' creado exitosamente!")
    safe_addstr(stdscr, 2, 0, f"Se procesaron {len(selected_files)} alabanzas.")
    safe_addstr(stdscr, 4, 0, "Presiona cualquier tecla para salir.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)