import config
from logger import logging
from pytube import YouTube
import subprocess
import urllib.request

def download_video(movie_dict: dict):
    if 'youtu.be' in movie_dict['link'] or 'youtube.com' in movie_dict['link']:
        try:
            yt = YouTube(movie_dict['link'])
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path=config.DOWNLOADDIR, filename=movie_dict['filename'].replace('.mp4', ''))
        except:
            pass
        else:
            logging.info(f'Downloaded {movie_dict["filename"]} via pytube')
    else:
        try:
            subprocess.run(f'ffmpeg -i "{movie_dict["link"]}" -c copy -bsf:a aac_adtstoasc "{config.DOWNLOADDIR + movie_dict["filename"]}"', shell=True)
        except:
            try:
                urllib.request.urlretrieve(movie_dict['link'], config.DOWNLOADDIR + movie_dict['filename'])
            except:
                pass
            else:
                logging.info(f'Downloaded {movie_dict["filename"]} via urllib')
        else:
            logging.info(f'Downloaded {movie_dict["filename"]} via ffmpeg')
        return movie_dict
