from django.conf import settings
import ffmpeg


def checkVideoUpload(infos_video):

    if infos_video['width'] < settings.CONSTANT["VIDEO"]["WIDTH"] \
            and infos_video['height'] < settings.CONSTANT["VIDEO"]["HEIGHT"]:
        return False

    return True

def getInformationsVideo(videoTemporyUpload):
    infos_video = {}

    try:
        probe = ffmpeg.probe(videoTemporyUpload.temporary_file_path())
    except ffmpeg.Error as e:
        return infos_video
        # print(e.stderr, file=sys.stderr)
        # sys.exit(1)

    video_stream = next(
        (stream for stream in probe['streams']
         if stream['codec_type'] == 'video'),
        None
    )
    if video_stream is None:
        return infos_video
        # print('No video stream found', file=sys.stderr)
        # sys.exit(1)

    infos_video['width'] = int(video_stream['width'])
    infos_video['height'] = int(video_stream['height'])
    infos_video['duration'] = float(video_stream['duration'])
    infos_video['num_frame'] = int(video_stream['nb_frames'])
    infos_video['size'] = videoTemporyUpload.size

    return infos_video