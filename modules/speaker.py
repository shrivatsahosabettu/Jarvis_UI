# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""

from typing import NoReturn

import pyttsx3

from modules.logger import logger
from modules.models import settings

audio_driver = pyttsx3.init()
voices = audio_driver.getProperty("voices")  # gets the list of voices available
voice_model = "Daniel" if settings.macos else "David"
for ind_d, voice_id in enumerate(voices):  # noqa
    if voice_id.name == voice_model or voice_model in voice_id.name:
        audio_driver.setProperty("voice", voices[ind_d].id)  # noqa
        break
else:
    logger.info("Using default voice model.")


def speak(text: str) -> NoReturn:
    """Calls ``audio_driver.say`` to speak a statement from the received text.

    Args:
        text: Takes the text that has to be spoken as an argument.
    """
    text = text.replace('\n', '\t').strip()
    if not text.endswith('.') or not text.endswith('!'):
        text = text + '!'
    audio_driver.say(text=text)
    audio_driver.runAndWait()
