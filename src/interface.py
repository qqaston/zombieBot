import colorama
from pathlib import Path

def show_main_menu():
    """Muestra el menú principal y devuelve la opción seleccionada."""
    print(colorama.Fore.CYAN + "\n======================================")
    print(colorama.Fore.CYAN + "       ZOMBIEBOT V1 - INTERFAZ")
    print(colorama.Fore.CYAN + "======================================")
    print("1. Iniciar Proceso (Todos los canales)")
    print("2. Iniciar Proceso (Canales personalizados)")
    print("3. Agregar Canal")
    print("4. Eliminar Canal")
    print("5. Salir")
    
    choice = input(colorama.Fore.YELLOW + "\nSelecciona una opción (1-5): " + colorama.Style.RESET_ALL)
    return choice

def get_channels_from_file(file_path):
    """Lee y devuelve la lista de canales limpios del archivo."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

def save_channels_to_file(file_path, channels):
    """Guarda la lista de canales en el archivo."""
    with open(file_path, 'w') as f:
        for channel in channels:
            f.write(f"{channel}\n")

def select_channels_ui(file_path):
    """Interfaz para seleccionar canales específicos."""
    channels = get_channels_from_file(file_path)
    if not channels:
        print(colorama.Fore.RED + "No hay canales registrados.")
        return []

    print(colorama.Fore.CYAN + "\n--- Selección de Canales ---")
    pad = len(str(len(channels)))
    for i, channel in enumerate(channels):
        print(f"{str(i+1).rjust(pad)}. {channel}")
    
    print("\nIngresa los números de los canales a procesar separados por coma (ej: 1, 3, 5)")
    print("O presiona ENTER para cancelar selección.")
    selection = input(colorama.Fore.YELLOW + "> " + colorama.Style.RESET_ALL)
    
    if not selection.strip():
        return []

    selected_indices = []
    try:
        parts = selection.split(',')
        for part in parts:
            idx = int(part.strip()) - 1
            if 0 <= idx < len(channels):
                selected_indices.append(idx)
    except ValueError:
        print(colorama.Fore.RED + "Entrada inválida.")
        return []
    
    return [channels[i] for i in selected_indices]

def add_channel_ui(file_path):
    """Interfaz para agregar un nuevo canal."""
    print(colorama.Fore.CYAN + "\n--- Agregar Nuevo Canal ---")
    print("Ingresa la URL del canal de Kick, Twitch, etc.")
    new_url = input(colorama.Fore.YELLOW + "URL: " + colorama.Style.RESET_ALL).strip()
    
    if not new_url:
        print(colorama.Fore.RED + "URL vacía, cancelando.")
        return

    channels = get_channels_from_file(file_path)
    if new_url in channels:
        print(colorama.Fore.YELLOW + "Este canal ya está en la lista.")
        return

    channels.append(new_url)
    save_channels_to_file(file_path, channels)
    print(colorama.Fore.GREEN + f"✅ Canal agregado: {new_url}")

def delete_channel_ui(file_path):
    """Interfaz para eliminar un canal."""
    channels = get_channels_from_file(file_path)
    if not channels:
        print(colorama.Fore.RED + "No hay canales para eliminar.")
        return

    print(colorama.Fore.CYAN + "\n--- Eliminar Canal ---")
    pad = len(str(len(channels)))
    for i, channel in enumerate(channels):
        print(f"{str(i+1).rjust(pad)}. {channel}")
    
    print("\nIngresa el número del canal a ELIMINAR (o ENTER para cancelar)")
    selection = input(colorama.Fore.YELLOW + "> " + colorama.Style.RESET_ALL)

    if not selection.strip():
        return

    try:
        idx = int(selection.strip()) - 1
        if 0 <= idx < len(channels):
            removed = channels.pop(idx)
            save_channels_to_file(file_path, channels)
            print(colorama.Fore.GREEN + f"🗑️ Canal eliminado: {removed}")
        else:
            print(colorama.Fore.RED + "Número de canal inválido.")
    except ValueError:
        print(colorama.Fore.RED + "Entrada inválida.")
