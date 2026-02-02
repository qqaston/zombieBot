import yt_dlp
import json
import colorama
import time
import shutil
import requests
from pathlib import Path

# Importar configuraciones
from config import DOWNLOADS_PATH, CLIP_DURATION_RANGE

# --- Removed Selenium Imports ---
# Se eliminó Selenium para no depender de Chrome instalado.

def download_clips(channels_source: str | list, num_clips: int = 5) -> list:
    """
    Descarga clips de una lista de canales o de un archivo.

    Args:
        channels_source (str | list): Ruta al archivo .txt o lista de URLs.
        num_clips (int): Número máximo de clips a descargar por canal.

    Returns:
        list: Una lista de diccionarios con metadatos de los clips.
    """
    # --- Verificación de Dependencias Críticas ---
    if not shutil.which('ffmpeg'):
        print(colorama.Fore.RED + "❌ Error Crítico: FFmpeg no está instalado o no se encuentra en el PATH del sistema.")
        return []
    
    DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
    
    channel_urls = []
    
    # Determinar si es archivo o lista directa
    if isinstance(channels_source, str):
        print(f"-> Iniciando descarga desde archivo '{channels_source}'...")
        try:
            with open(channels_source, 'r') as f:
                channel_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(colorama.Fore.RED + f"❌ Error: No se encontró el archivo '{channels_source}'.")
            return []
    elif isinstance(channels_source, list):
        print(f"-> Iniciando descarga de {len(channels_source)} canales seleccionados...")
        channel_urls = channels_source
    else:
        print(colorama.Fore.RED + "❌ Error: Fuente de canales inválida.")
        return []

    if not channel_urls:
        print(colorama.Fore.YELLOW + "La lista de canales está vacía.")
        return []

    downloaded_clips_info = []
    min_duration, max_duration = CLIP_DURATION_RANGE

    # Filtro de duración para yt-dlp
    duration_filter = f"duration >= {min_duration} & duration <= {max_duration}"

    for channel_url in channel_urls:
        print(colorama.Fore.BLUE + f"\nBuscando clips para el canal: {channel_url}")
        
        kick_clips_data = [] # Lista de clips de Kick encontrados (diccionarios con metadata)
        urls_to_process = [] # Lista standard para yt-dlp (Twitch, YouTube, URL directa)

        # --- LÓGICA DE OBTENCIÓN DE URLS ---
        if "twitch.tv" in channel_url:
            # Para Twitch, yt-dlp puede manejar la página de clips directamente.
            twitch_clips_page = f"{channel_url.rstrip('/')}/clips?filter=clips&range=24hr"
            urls_to_process.append(twitch_clips_page)
            print(f"  -> Apuntando a la página de clips de Twitch: {twitch_clips_page}")
        elif "kick.com" in channel_url:
            # Kick API Logic
            kick_clips_data = _get_kick_clips_api(channel_url, num_clips)
        else:
            # Es una URL directa a un video/clip, usarla tal cual.
            urls_to_process.append(channel_url)

        # --- LÓGICA DE DESCARGA (YT-DLP STANDARD) ---
        if urls_to_process:
             for i, clip_url in enumerate(urls_to_process):
                # Para no exceder el num_clips total si es una playlist de Twitch
                if i >= num_clips and "twitch.tv" not in clip_url:
                    break

                print(colorama.Fore.CYAN + f"  -> Procesando URL: {clip_url}")
                
                output_template = DOWNLOADS_PATH / '%(uploader)s - %(title)s [%(id)s].%(ext)s'
                is_playlist = "twitch.tv/clips" in clip_url

                ydl_opts = {
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                    'outtmpl': str(output_template),
                    'playlist_items': f'1-{num_clips}' if is_playlist else None,
                    'match_filter': yt_dlp.utils.match_filter_func(duration_filter),
                    'ignoreerrors': True,
                    'noprogress': True,
                    'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
                    'writeinfojson': True,
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(clip_url, download=True)

                        if not info:
                            print(colorama.Fore.YELLOW + f"    - No se pudo extraer información para la URL.")
                            continue

                        entries = info.get('entries', [info])

                        if not entries or all(e is None for e in entries):
                            print(colorama.Fore.YELLOW + f"    - No se encontraron clips que cumplan los criterios en esta URL.")
                            continue

                        for entry in entries:
                            if not entry: continue
                            json_path = Path(ydl.prepare_filename(entry)).with_suffix('.info.json')
                             # Si yt-dlp cambia el contenedor, el archivo podría ser .mp4 aunque el template diga .webm, etc.
                            # Buscamos el info.json que se escribe con 'writeinfojson': True
                            
                            # NOTA: yt-dlp a veces no escribe el json si falla algo, pero si descarga...
                            # Intentamos deducir el path del video.
                            
                            if json_path.exists():
                                with open(json_path, 'r', encoding='utf-8') as jf:
                                    metadata = json.load(jf)
                                video_filepath = json_path.with_suffix('.mp4')
                            else:
                                # Fallback si no hay json (no debería pasar con writeinfojson=True si descarga ok)
                                video_filepath = Path(ydl.prepare_filename(entry))
                                metadata = entry

                            if video_filepath.exists():
                                print(colorama.Fore.GREEN + f"    ✓ Descargado y convertido: {metadata.get('title')}")
                                clip_info = {
                                    'video_path': str(video_filepath),
                                    'title': metadata.get('title', 'Sin Título'),
                                    'author': metadata.get('uploader', 'Desconocido'),
                                }
                                downloaded_clips_info.append(clip_info)

                except Exception as e:
                    print(colorama.Fore.RED + f"  ❌ Ocurrió un error inesperado con {clip_url}: {e}")

        # --- LÓGICA DE DESCARGA (KICK API) ---
        if kick_clips_data:
            print(colorama.Fore.CYAN + f"  -> Procesando {len(kick_clips_data)} clips de Kick encontrados vía API...")
            for clip_data in kick_clips_data:
                video_url = clip_data['video_url'] # m3u8 url
                title = clip_data['title']
                author = clip_data['author']
                clip_id = clip_data['id']
                
                # Sanitizar nombre de archivo
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                safe_author = "".join([c for c in author if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"{safe_author} - {safe_title} [{clip_id}].mp4"
                output_path = DOWNLOADS_PATH / filename

                if output_path.exists():
                    print(colorama.Fore.YELLOW + f"    - El archivo ya existe: {filename}")
                    downloaded_clips_info.append({
                        'video_path': str(output_path),
                        'title': title,
                        'author': author
                    })
                    continue

                print(colorama.Fore.CYAN + f"    Downloading: {title}...")
                
                # Descargar m3u8 con yt-dlp
                ydl_opts_kick = {
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
                    'outtmpl': str(output_path),
                    'noprogress': True,
                    # No filter needed as we already filtered by API/selection logic ideally, 
                    # but simple duration check handled by API? 
                    # Kick API returns 'duration', we can check here.
                }

                try:
                   with yt_dlp.YoutubeDL(ydl_opts_kick) as ydl:
                        ydl.download([video_url])
                    
                   if output_path.exists():
                        print(colorama.Fore.GREEN + f"    ✓ Descarga Kick completada: {title}")
                        downloaded_clips_info.append({
                            'video_path': str(output_path),
                            'title': title,
                            'author': author
                        })
                   else:
                        print(colorama.Fore.RED + f"    ❌ Falló descarga de: {title}")

                except Exception as e:
                     print(colorama.Fore.RED + f"    ❌ Error descargando clip de Kick: {e}")


    print(colorama.Fore.GREEN + f"\n✅ Descarga completada. Se obtuvieron {len(downloaded_clips_info)} clips.")
    return downloaded_clips_info

def _get_kick_clips_api(channel_url: str, num_clips: int) -> list[dict]:
    """
    Obtiene metadatos de clips usando la API v2 de Kick.
    No requiere Selenium.
    """
    # Robust slug extraction: handles https://kick.com/slug, https://kick.com/slug/clips, etc.
    try:
        # Remove trailing slash first
        clean_url = channel_url.rstrip('/')
        if 'kick.com/' in clean_url:
            slug = clean_url.split('kick.com/')[-1].split('/')[0]
        else:
            # Fallback for unexpected formats
            slug = clean_url.split('/')[-1]
    except Exception:
        slug = channel_url.rstrip('/').split('/')[-1]

    api_url = f"https://kick.com/api/v2/channels/{slug}/clips"
    
    # Headers para simular navegador real y evitar 403
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://kick.com/"
    }

    try:
        print(colorama.Fore.CYAN + f"  -> Consultando Kick API para: {slug}...")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(colorama.Fore.RED + f"  ❌ API Error {response.status_code}: {response.text[:100]}")
            return []

        data = response.json()
        clips = data.get('clips', [])
        
        valid_clips = []
        for clip in clips:
            # Filtrar por duración (ej. 10s - 180s)
            duration = clip.get('duration', 0)
            if not (10 <= duration <= 180): # Usar constantes si es posible
                continue
                
            valid_clips.append({
                'title': clip.get('title', 'Kick Clip'),
                'author': clip.get('channel', {}).get('username', slug),
                'video_url': clip.get('video_url') or clip.get('clip_url'), # m3u8
                'id': clip.get('id'),
                'duration': duration
            })
            
            if len(valid_clips) >= num_clips:
                break
                
        print(colorama.Fore.GREEN + f"  -> Encontrados {len(valid_clips)} clips válidos vía API.")
        return valid_clips

    except Exception as e:
        print(colorama.Fore.RED + f"  ❌ Error de conexión con Kick API: {e}")
        return []