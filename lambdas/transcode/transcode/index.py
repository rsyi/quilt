"""
Generate video previews for videos in S3.
"""
import os
import pathlib
import requests
import subprocess
import tempfile

from t4_lambda_shared.decorator import api, validate
from t4_lambda_shared.utils import get_default_origins, make_json_response


SCHEMA = {
    'type': 'object',
    'properties': {
        'url': {
            'type': 'string'
        }
    },
    'required': ['url'],
    'additionalProperties': False
}

FFMPEG = pathlib.Path(__file__).parent / 'exodus/bin/ffmpeg'
FFMPEG_TIME_LIMIT = 20
DURATION = 5
WIDTH = 320
HEIGHT = 240


@api(cors_origins=get_default_origins())
@validate(SCHEMA)
def lambda_handler(request):
    """
    Generate thumbnails for images in S3
    """
    url = request.args['url']

    # with tempfile.NamedTemporaryFile() as input_file, \
    #      tempfile.NamedTemporaryFile(suffix='.mp4') as output_file:
    #     with requests.get(url, stream=True) as r:
    #         r.raise_for_status()
    #         for chunk in r.iter_content(chunk_size=8192):
    #             if chunk: # filter out keep-alive new chunks
    #                 input_file.write(chunk)
    #         input_file.flush()

    with tempfile.NamedTemporaryFile(suffix='.mp4') as output_file:
        subprocess.check_call([
            FFMPEG,
            "-t", str(DURATION),
            "-i", url,
            "-vf", f"scale=w={WIDTH}:h={HEIGHT}:force_original_aspect_ratio=decrease",
            "-timelimit", str(FFMPEG_TIME_LIMIT),
            "-y",  # Overwrite output file
            output_file.name
        ], stdin=subprocess.DEVNULL)

        data = output_file.read()

    return 200, data, {'Content-Type': 'video/mp4'}