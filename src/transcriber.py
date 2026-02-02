def transcribe_and_subtitle(video_path: str):
    """
    Toma un video, transcribe el audio y añade subtítulos "quemados".
    
    Esta es una implementación de marcador de posición.
    
    Args:
        video_path (str): Ruta al video base (sin subtítulos).
    """
    print(f"-> Transcribiendo y subtitulando: {video_path}")
    
    # TODO: Implementar la transcripción y subtitulado.
    # - Extraer audio.
    # - Transcribir con faster-whisper.
    # - Generar y componer TextClips con moviepy.
    
    final_video_path = video_path.replace(".mp4", "_subtitled.mp4")
    print(f"-> (Simulación) Video con subtítulos guardado en: {final_video_path}")
    
    return final_video_path