import sys
from django.conf import settings
import ffmpeg


def checkVideoUpload(videoTemporyUpload):
    try:
        probe = ffmpeg.probe(videoTemporyUpload.temporary_file_path())
    except ffmpeg.Error as e:
        return False
        # print(e.stderr, file=sys.stderr)
        # sys.exit(1)

    video_stream = next(
        (stream for stream in probe['streams']
         if stream['codec_type'] == 'video'),
        None
    )
    if video_stream is None:
        return False
        # print('No video stream found', file=sys.stderr)
        # sys.exit(1)

    width = int(video_stream['width'])
    height = int(video_stream['height'])
    num_frames = int(video_stream['nb_frames'])

    if width < settings.CONSTANT["VIDEO"]["WIDTH"] \
            and height < settings.CONSTANT["VIDEO"]["HEIGHT"]:
        return False

    print(video_stream)

    return True