import yt_dlp
import os
import re
import logging
from flask import Flask, request, send_file
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def clean_filename(title):
    try:
        title = re.sub(r'[^\x00-\x7FáéíóúÁÉÍÓÚâêîôÂÊÎÔãõÃÕçÇ&]', '', title)
        title = re.sub(r'[<>:"/\\|?*@]', '', title)
        title = title.strip()
        title = " ".join(title.split())
        return title
    
    except Exception as e:
        logger.error(f"Erro ao limpar o título: {e}")
        now = datetime.now()
        return f"audio_{now.strftime('%Y_%m_%d-%H_%M_%S')}"

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        logger.error("URL do vídeo não fornecida.")
        return "URL do vídeo não fornecida.", 400

    try:
        logger.info(f"Extraindo informações do vídeo: {video_url}")
        with yt_dlp.YoutubeDL({'logger': logger}) as ydl:
            info = ydl.extract_info(video_url, download=False)

        if not info or not isinstance(info, dict):
            logger.error("Informações do vídeo não foram retornadas corretamente.")
            return "Erro ao extrair informações do vídeo.", 500

        title = info.get('title', 'audio')
        if not title:
            logger.error("Título do vídeo não encontrado.")
            return "Erro ao obter o título do vídeo.", 500

        logger.info(f"Título do vídeo: {title}")

        clean_title = clean_filename(title)
        logger.info(f"Título limpo: {clean_title}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_DIR, f'{clean_title}.%(ext)s'),
            'logger': logger,
        }

        logger.info("Iniciando o download do áudio...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        output_file = os.path.join(DOWNLOAD_DIR, f'{clean_title}.mp3')
        if not os.path.exists(output_file):
            logger.error(f"Arquivo de saída não encontrado: {output_file}")
            return "Erro ao criar o arquivo de áudio.", 500

        logger.info(f"Enviando arquivo: {output_file}")
        return send_file(output_file, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"Erro ao baixar o vídeo: {e}")
        return f"Erro ao baixar o vídeo: {str(e)}", 500
    except Exception as e:
        logger.error(f"Erro inesperado: {e}", exc_info=True)
        return f"Erro inesperado: {str(e)}", 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
