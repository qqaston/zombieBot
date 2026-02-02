import colorama
import sys

# Importar módulos
from src.downloader import download_clips
from src.editor import edit_video
from src.transcriber import transcribe_and_subtitle
from src.uploader import upload_to_tiktok
import src.interface as interface

CHANNELS_FILE = "channels.txt"

def process_clips(clips_info):
    """Procesa una lista de clips con lógica de pausa."""
    if not clips_info:
        print(colorama.Fore.YELLOW + "No se descargaron clips. Volviendo al menú.")
        return

    total_clips = len(clips_info)
    print(colorama.Fore.CYAN + f"\n⬇️  Se descargaron {total_clips} clips. Iniciando procesamiento...")

    i = 0
    while i < total_clips:
        clip_info = clips_info[i]
        try:
            print(colorama.Fore.CYAN + f"\n🎬 Procesando clip {i+1}/{total_clips}: {clip_info.get('title', 'Sin Título')}")
            
            # --- EDITOR ---
            print(colorama.Fore.CYAN + "   2️⃣  Editor...")
            base_video_path = edit_video(clip_info)
            
            # --- TRANSCRIBER ---
            print(colorama.Fore.CYAN + "   3️⃣  Transcriber...")
            final_video_path = transcribe_and_subtitle(base_video_path)
            
            # --- UPLOADER ---
            print(colorama.Fore.CYAN + "   4️⃣  Uploader...")
            upload_to_tiktok(final_video_path, clip_info)
            
            print(colorama.Fore.GREEN + f"   ✅ Clip completado.")
            i += 1

        except KeyboardInterrupt:
            print(colorama.Fore.YELLOW + "\n\n⏸️  PROCESO PAUSADO POR EL USUARIO")
            while True:
                choice = input(colorama.Fore.YELLOW + "Elige una opción: (c)ontinuar, (s)top/cancelar: " + colorama.Style.RESET_ALL).lower().strip()
                if choice == 'c':
                    print(colorama.Fore.GREEN + "▶️  Reanudando...")
                    break # Sale del bucle de pausa y reintenta el mismo clip o sigue (idealmente reintenta si falló a medias, pero aquí sigue con el siguiente paso si ya acabó uno, o re-ejecuta el bloque si estaba a medias. Ojo: si interrumpe a mitad de función, puede quedar estado inconsistente. Simplificación: asume reanudar donde dejó o reintentar loop)
                    # En este while simple, al hacer continue del outer loop, volvería a intentar el MISMO 'i' si no incrementamos 'i'.
                    # Pero el KeyboardInterrupt salta fuera del try.
                    # Así que no incrementamos 'i' aquí.
                    break 
                elif choice == 's':
                    print(colorama.Fore.RED + "⏹️  Proceso cancelado. Volviendo al menú principal.")
                    return # Sale de la función process_clips
                else:
                    print("Opción no válida.")
        
        except Exception as e:
            print(colorama.Fore.RED + f"❌ Error procesando el clip {clip_info.get('title')}: {e}")
            i += 1 # Continuar con el siguiente clip ante error
            continue

def main():
    colorama.init(autoreset=True)

    while True:
        choice = interface.show_main_menu()
        
        if choice == '1': # Iniciar (Todos)
            print(colorama.Fore.GREEN + "\n🚀 Iniciando con TODOS los canales...")
            clips = download_clips(CHANNELS_FILE)
            process_clips(clips)
            
        elif choice == '2': # Iniciar (Custom)
            selected_channels = interface.select_channels_ui(CHANNELS_FILE)
            if selected_channels:
                print(colorama.Fore.GREEN + f"\n🚀 Iniciando con {len(selected_channels)} canales seleccionados...")
                clips = download_clips(selected_channels)
                process_clips(clips)
            else:
                print(colorama.Fore.YELLOW + "Cancelado o sin selección.")

        elif choice == '3': # Agregar Canal
            interface.add_channel_ui(CHANNELS_FILE)
            
        elif choice == '4': # Eliminar Canal
            interface.delete_channel_ui(CHANNELS_FILE)
            
        elif choice == '5': # Salir
            print(colorama.Fore.GREEN + "👋 Saliendo...")
            sys.exit(0)
            
        else:
            print(colorama.Fore.RED + "Opción inválida, intenta de nuevo.")

if __name__ == "__main__":
    main()