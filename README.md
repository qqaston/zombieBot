# 🧟 ZombieBot V1

ZombieBot es un bot automatizado diseñado para **descargar, editar y subir** clips de plataformas de streaming (Kick, Twitch, etc.) a TikTok/Youtube Shorts.

## 🚀 Funcionalidades

*   **Descarga Automática**: Obtiene clips populares o recientes desde una lista de canales (`channels.txt`).
*   **Edición de Video**: Recorta y adapta los clips a formato vertical (9:16) automáticamente.
*   **Transcripción y Subtítulos**: Genera subtítulos automáticos usando IA (Faster-Whisper).
*   **Interfaz Interactiva**:
    *   Menú CLI para gestionar el bot.
    *   Selección de todos los canales o personalizados.
    *   Agregar/Eliminar canales desde la consola.
    *   **Pausa/Reanudar**: Control total del proceso con `Ctrl+C`.

## ⚙️ Instalación

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tu-usuario/zombiebot-v1.git
    cd zombiebot-v1
    ```

2.  **Crear y activar entorno virtual**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Linux/Mac
    # venv\Scripts\activate   # En Windows
    ```

3.  **Instalar dependencias**:
    Asegúrate de tener **FFmpeg** instalado en tu sistema (`sudo apt install ffmpeg`).
    ```bash
    pip install -r requirements.txt
    ```

## 🔧 Configuración

1.  Copia el archivo de ejemplo:
    ```bash
    cp .env.example .env
    ```
2.  Edita el archivo `.env` con tus preferencias:
    *   `VIDEO_CODEC`: `h264_nvenc` (NVIDIA GPU) o `libx264` (CPU).
    *   `CHROME_PROFILE_PATH`: Ruta a tu perfil de Chrome (opcional para auth).

## ▶️ Ejecución

Para iniciar la interfaz interactiva:

```bash
# Con el entorno activado
python main.py

# O directamente
./venv/bin/python3 main.py
```

## 📋 Uso
1.  **Iniciar**: Elige procesar todos los canales o una selección específica.
2.  **Pausar**: Presiona `Ctrl+C` en cualquier momento para mostrar el menú de pausa.
