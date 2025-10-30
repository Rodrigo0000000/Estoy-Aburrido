import flask
import pytubefix
import ffmpeg
import os
import re

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/calidades', methods=['POST'])
def calidades():
    try:
        calidades = []
        tags = []
        url = flask.request.form.get('url')
        if not url or url.strip() == '':
            return flask.render_template('index.html')
        else:
            video_info = None
            video = pytubefix.YouTube(url)
            miniatura = video.thumbnail_url
            calidad = video.streams.filter(file_extension='mp4').order_by('resolution').desc()
            resoluciones_vistas = set()
            video_info = {
            'title': video.title,
            'thumbnail': video.thumbnail_url,
            'video_url': video.watch_url
            }
            
            
            for stream in calidad:
                if stream.resolution not in resoluciones_vistas:
                    calidades.append(stream.resolution)
                    tags.append(stream.itag)
                    resoluciones_vistas.add(stream.resolution)
                    print(stream.resolution, stream.itag)

        es_short = "shorts" in url
        return flask.render_template('index.html', calidades=calidades, itag=tags, url=url, es_short=es_short, miniatura=miniatura, video_info=video_info)

    except Exception as e:
        print(f"Error al mostrar calidades: {e}")
        return flask.render_template('index.html')

@app.route('/descargar', methods=['POST'])
def descargar():
    try:
        url = flask.request.form.get('url')
    
        itag = flask.request.form.get('itag')

        if not itag or not url or "shorts" in url:
            return flask.render_template('index.html')

        itag = int(itag)
        video = pytubefix.YouTube(url)
        
        video_stream = video.streams.get_by_itag(itag)
        if video_stream is None:
            return flask.render_template('index.html')

        titulo_limpio = limpiar_nombre(video.title)
        video_path = video_stream.download(filename=f'{titulo_limpio}.mp4')

        audio_stream = video.streams.filter(only_audio=True).desc().first()
        audio_path = audio_stream.download(filename=f'{titulo_limpio}.mp3')

        output_path = f"{titulo_limpio} descargado.mp4"

        ffmpeg.output(
            ffmpeg.input(video_path),
            ffmpeg.input(audio_path),
            output_path,
            vcodec='copy',
            acodec='aac'
        ).run(overwrite_output=True)

        os.remove(video_path)
        os.remove(audio_path)

        return flask.send_file(output_path, as_attachment=True)
    except Exception as e:
        print(f"Error al descargar: {e}")
        return flask.render_template('index.html')

@app.route('/audio', methods=['POST'])
def descargar_audio():
    try:
        url = flask.request.form.get('url')
        video = pytubefix.YouTube(url)

        audio_stream = video.streams.filter(only_audio=True).desc().first()
        titulo_limpio = limpiar_nombre(audio_stream.title)
        audio_path = audio_stream.download(filename=f'{titulo_limpio}.mp4')

        return flask.send_file(audio_path, as_attachment=True)
    except Exception as e:
        print(f"Error al descargar: {e}")
        return flask.render_template('index.html')

@app.route('/shorts', methods=['POST'])
def descargar_shorts():
    try:
        url = flask.request.form.get('url')
        itag = flask.request.form.get('itag')

        if not itag or not url:
            return flask.render_template('index.html')

        itag = int(itag)
        video_id = obtener_id_youtube(url)
        if not video_id:
            return flask.render_template('index.html')

        formato = f"https://www.youtube.com/watch?v={video_id}"
        video = pytubefix.YouTube(formato)

        video_stream = video.streams.get_by_itag(itag)
        if video_stream is None:
            return flask.render_template('index.html')

        titulo_limpio = limpiar_nombre(video.title)
        video_path = video_stream.download(filename=f'{titulo_limpio}.mp4')

        audio_stream = video.streams.filter(only_audio=True).desc().first()
        audio_path = audio_stream.download(filename=f'{titulo_limpio}.mp3')

        output_path = f"{titulo_limpio} descargado.mp4"


        output_path = f"{titulo_limpio} descargado.mp4"
        ffmpeg.output(
            ffmpeg.input(video_path),
            ffmpeg.input(audio_path),
            output_path,
            vcodec='copy',
            acodec='aac'
        ).run(overwrite_output=True)

        os.remove(video_path)
        os.remove(audio_path)

        return flask.send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"Error al descargar: {e}")
        return flask.render_template('index.html')

def obtener_id_youtube(url):
    regex = r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/))([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def limpiar_nombre(nombre):
    lista_sin_caracteres = [re.sub('[^a-zA-Z0-9\s()]', '', string).strip() for string in nombre.split()]

    lista_limpiada= [string for string in lista_sin_caracteres if string]

    return " ".join(lista_limpiada)

if __name__ == '__main__':
    app.run(debug=True)


