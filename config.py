import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# --- GENERAL ---
BASE_DIR = Path(__file__).resolve().parent

# --- RUTAS ---
# Creando las rutas absolutas para evitar problemas de ejecución desde distintas ubicaciones
ASSETS_PATH = BASE_DIR / "assets"
GAMEPLAY_PATH = ASSETS_PATH / "gameplay"
OVERLAYS_PATH = ASSETS_PATH / "overlays"
MUSIC_PATH = ASSETS_PATH / "music"

DOWNLOADS_PATH = BASE_DIR / "downloads"
TEMP_PATH = BASE_DIR / "temp"
OUTPUT_PATH = BASE_DIR / "output"

# --- VIDEO ---
TARGET_RESOLUTION = (1080, 1920)  # 9:16 aspect ratio
VIDEO_BITRATE = "8000k"  # Bitrate para el video final (ej. '5000k', '8000k')
# Codec de video a usar. 'h264_nvenc' para aceleración por GPU NVIDIA.
# Usa 'libx264' si no tienes GPU NVIDIA.
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")

# --- EDITOR ---
CLIP_DURATION_RANGE = (10, 180)  # Min/Max duración del clip en segundos (10s a 3min)
GAMEPLAY_VOLUME = 0.1  # 10% del volumen original
MUSIC_VOLUME = 0.05  # 5% del volumen original

# --- TRANSCRIPCIÓN ---
# Modelo de faster-whisper. Opciones: "tiny", "base", "small", "medium", "large-v2"
TRANSCRIPTION_MODEL = "small"
TRANSCRIPTION_DEVICE = "cuda"  # "cuda" (para GPU NVIDIA) o "cpu"

# NOTA: Para TextClip en MoviePy, necesitas tener ImageMagick instalado.
SUBTITLE_FONT = "Komika-Axis"  # Asegúrate que la fuente esté instalada en tu sistema
SUBTITLE_FONT_SIZE = 72
SUBTITLE_COLOR = "yellow"
SUBTITLE_STROKE_COLOR = "black"
SUBTITLE_STROKE_WIDTH = 2

# --- UPLOADER ---
# Ruta al perfil de Chrome para que Selenium pueda reusar cookies y sesión.
# Se lee de la variable de entorno CHROME_PROFILE_PATH
CHROME_PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH", "")