python ./transmission.py
ffmpeg -f s16le -ar 8000 -ac 1 -i data.pcm -ar 8000 -ac 1 out.wav
afplay ./out.wav
