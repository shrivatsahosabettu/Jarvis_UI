# noinspection PyUnresolvedReferences
"""Module to kick off wake word detection.

>>> Starter

"""

import os
import string
import struct
from datetime import datetime
from multiprocessing.managers import DictProxy  # noqa
from typing import NoReturn, Union

import pvporcupine
from pyaudio import PyAudio, Stream, paInt16

from jarvis_ui.executables import display, listener, speaker
from jarvis_ui.executables.api_handler import make_request
from jarvis_ui.modules.config import config
from jarvis_ui.modules.logger import logger
from jarvis_ui.modules.models import env, fileio, settings
from jarvis_ui.modules.playsound import playsound


def processor() -> Union[str, None]:
    """Processes the request after wake word is detected.

    Returns:
        bool:
        Returns a ``True`` flag if a manual stop is requested.
    """
    if phrase := listener.listen():
        logger.info(f"Request: {phrase}")
        display.write_screen(f"Request: {phrase}")
        if "restart" in phrase.lower():
            logger.info("User requested to restart.")
            playsound(sound=fileio.restart)
            display.write_screen("Restarting...")
            return "RESTART"
        if "stop running" in phrase.lower():
            logger.info("User requested to stop.")
            playsound(sound=fileio.shutdown)
            display.write_screen("Shutting down")
            return "STOP"
        if not config.keywords:
            logger.warning("keywords are not loaded yet, restarting")
            playsound(sound=fileio.connection_restart)
            display.write_screen("Trying to re-establish connection with Server...")
            return "RESTART"
        if response := make_request(path='offline-communicator',
                                    data={'command': phrase, 'native_audio': env.native_audio,
                                          'speech_timeout': env.speech_timeout}):
            if response is True:
                logger.info("Response received as audio.")
                display.write_screen("Response received as audio.")
                playsound(sound=fileio.speech_wav_file)
                os.remove(fileio.speech_wav_file)
                return
            response = response.get('detail', '')
            logger.info(f"Response: {response}")
            display.write_screen(f"Response: {response}")
            speaker.speak(text=response)
        else:
            playsound(sound=fileio.failed)
            return "RESTART"


class Activator:
    """Awaits for the keyword ``Jarvis`` and triggers ``initiator`` when heard.

    >>> Activator

    See Also:
        - Creates an input audio stream from a microphone, monitors it, and detects the specified wake word.
        - After processing the phrase, the converted text is sent as response to the API.
    """

    def __init__(self):
        """Initiates Porcupine object for hot word detection.

        See Also:
            - Instantiates an instance of Porcupine object and monitors audio stream for occurrences of keywords.
            - A higher sensitivity results in fewer misses at the cost of increasing the false alarm rate.
            - sensitivity: Tolerance/Sensitivity level. Takes argument or env var ``sensitivity`` or defaults to ``0.5``

        References:
            - `Audio Overflow <https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.read>`__ handling.
        """
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in env.wake_words]
        self.py_audio = PyAudio()
        arguments = {
            "library_path": pvporcupine.LIBRARY_PATH,
            "sensitivities": env.sensitivity
        }
        if settings.legacy:
            arguments["keywords"] = env.wake_words
            arguments["model_file_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_file_paths"] = keyword_paths
        else:
            arguments["model_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_paths"] = keyword_paths

        self.detector = pvporcupine.create(**arguments)
        self.audio_stream = self.open_stream()
        label = ', '.join([f'{string.capwords(wake)!r}: {sens}' for wake, sens in
                           zip(env.wake_words, env.sensitivity)])
        self.label = f"Awaiting: [{label}]"

    def __del__(self) -> NoReturn:
        """Invoked when the run loop is exited or manual interrupt.

        See Also:
            - Releases resources held by porcupine.
            - Closes audio stream.
            - Releases port audio resources.
        """
        self.detector.delete()
        if self.audio_stream and self.audio_stream.is_active():
            self.py_audio.close(stream=self.audio_stream)
            self.audio_stream.close()
        self.py_audio.terminate()

    def open_stream(self) -> Stream:
        """Initializes an audio stream.

        Returns:
            Stream:
            PyAudio stream.
        """
        return self.py_audio.open(
            rate=self.detector.sample_rate,
            channels=1,
            format=paInt16,
            input=True,
            frames_per_buffer=self.detector.frame_length,
            input_device_index=env.microphone_index
        )

    def executor(self, status_manager: DictProxy):
        """Closes the audio stream and calls the processor."""
        logger.debug(f"Detected {settings.bot} at {datetime.now()}")
        status_manager["LOCKED"] = True
        logger.debug("Restart locked")
        playsound(sound=fileio.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        processed = processor()
        if processed == "STOP":
            self.audio_stream = None
            raise KeyboardInterrupt
        if processed == "RESTART":
            status_manager["LOCKED"] = None
            while True:
                pass  # To ensure the listener doesn't end so that, the main process can kill and restart
        status_manager["LOCKED"] = False
        logger.debug("Restart released")
        self.audio_stream = self.open_stream()
        display.flush_screen()

    def start(self, status_manager: DictProxy) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        logger.info(f"Starting wake word detector with sensitivity: {env.sensitivity}")
        while True:
            display.write_screen(self.label)
            pcm = struct.unpack_from("h" * self.detector.frame_length,
                                     self.audio_stream.read(num_frames=self.detector.frame_length,
                                                            exception_on_overflow=False))
            result = self.detector.process(pcm=pcm)
            if result is False or result < 0:
                continue
            self.executor(status_manager=status_manager)
