"""
module_tts.py

Text-to-Speech (TTS) module for TARS-AI application.

Handles TTS functionality to convert text into audio using:
- Azure Speech SDK
- Local tools (e.g., espeak-ng)
- Server-based TTS systems

"""

import requests
import os
from datetime import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from io import BytesIO
import asyncio
import threading
import json

from modules.module_messageQue import queue_message

# Conditional TTS module imports - not all are available on all devices
text_to_speech_with_pipelining_piper = None
text_to_speech_with_pipelining_silero = None
text_to_speech_with_pipelining_espeak = None
text_to_speech_with_pipelining_alltalk = None
text_to_speech_with_pipelining_elevenlabs = None
text_to_speech_with_pipelining_azure = None
text_to_speech_with_pipelining_openai = None
text_to_speech_with_pipelining_minimax = None

try:
    from vosk import KaldiRecognizer, SetLogLevel, Model

    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    from modules.module_piper import text_to_speech_with_pipelining_piper as _piper

    text_to_speech_with_pipelining_piper = _piper
except ImportError:
    pass

try:
    from modules.module_silero import text_to_speech_with_pipelining_silero as _silero

    text_to_speech_with_pipelining_silero = _silero
except ImportError:
    pass

try:
    from modules.module_espeak import text_to_speech_with_pipelining_espeak as _espeak

    text_to_speech_with_pipelining_espeak = _espeak
except ImportError:
    pass

try:
    from modules.module_alltalk import (
        text_to_speech_with_pipelining_alltalk as _alltalk,
    )

    text_to_speech_with_pipelining_alltalk = _alltalk
except ImportError:
    pass

try:
    from modules.module_elevenlabs import (
        text_to_speech_with_pipelining_elevenlabs as _elevenlabs,
    )

    text_to_speech_with_pipelining_elevenlabs = _elevenlabs
except ImportError:
    pass

try:
    from modules.module_azure import text_to_speech_with_pipelining_azure as _azure

    text_to_speech_with_pipelining_azure = _azure
except ImportError:
    pass

try:
    from modules.module_openai import text_to_speech_with_pipelining_openai as _openai

    text_to_speech_with_pipelining_openai = _openai
except ImportError:
    pass

try:
    from modules.module_minimax import (
        text_to_speech_with_pipelining_minimax as _minimax,
    )

    text_to_speech_with_pipelining_minimax = _minimax
except ImportError:
    pass

from modules.module_stt import get_stt_manager


def update_tts_settings(ttsurl):
    url = f"{ttsurl}/set_tts_settings"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "stream_chunk_size": 100,
        "temperature": 0.75,
        "speed": 1,
        "length_penalty": 1.0,
        "repetition_penalty": 5,
        "top_p": 0.85,
        "top_k": 50,
        "enable_text_splitting": True,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            queue_message(f"LOAD: TTS Settings updated successfully.")
        else:
            queue_message(
                f"ERROR: Failed to update TTS settings. Status code: {response.status_code}"
            )
            queue_message(f"INFO: Response: {response.text}")
    except Exception as e:
        queue_message(f"ERROR: TTS update failed: {e}")


def play_audio_stream(
    tts_stream, samplerate=22050, channels=1, gain=1.0, normalize=False
):
    try:
        with sd.OutputStream(
            samplerate=samplerate, channels=channels, dtype="int16", blocksize=4096
        ) as stream:
            for chunk in tts_stream:
                if chunk:
                    audio_data = np.frombuffer(chunk, dtype="int16")

                    if normalize:
                        max_value = np.max(np.abs(audio_data))
                        if max_value > 0:
                            audio_data = audio_data / max_value * 32767

                    audio_data = np.clip(audio_data * gain, -32768, 32767).astype(
                        "int16"
                    )
                    stream.write(audio_data)
                else:
                    queue_message(f"ERROR: Received empty chunk.")
    except Exception as e:
        queue_message(f"ERROR: Error during audio playback: {e}")


async def generate_tts_audio(
    text,
    ttsoption,
    is_wakeword=False,
    azure_api_key=None,
    azure_region=None,
    ttsurl=None,
    toggle_charvoice=True,
    tts_voice=None,
):
    try:
        if ttsoption == "azure" and text_to_speech_with_pipelining_azure:
            async for chunk in text_to_speech_with_pipelining_azure(text):
                yield chunk

        elif ttsoption == "espeak" and text_to_speech_with_pipelining_espeak:
            async for chunk in text_to_speech_with_pipelining_espeak(text):
                yield chunk

        elif ttsoption == "alltalk" and text_to_speech_with_pipelining_alltalk:
            async for chunk in text_to_speech_with_pipelining_alltalk(text):
                yield chunk

        elif ttsoption == "piper" and text_to_speech_with_pipelining_piper:
            async for chunk in text_to_speech_with_pipelining_piper(text):
                yield chunk

        elif ttsoption == "elevenlabs" and text_to_speech_with_pipelining_elevenlabs:
            async for chunk in text_to_speech_with_pipelining_elevenlabs(
                text, is_wakeword
            ):
                yield chunk

        elif ttsoption == "minimax" and text_to_speech_with_pipelining_minimax:
            async for chunk in text_to_speech_with_pipelining_minimax(
                text, is_wakeword
            ):
                yield chunk

        elif ttsoption == "silero" and text_to_speech_with_pipelining_silero:
            async for chunk in text_to_speech_with_pipelining_silero(text):
                yield chunk

        elif ttsoption == "openai" and text_to_speech_with_pipelining_openai:
            async for chunk in text_to_speech_with_pipelining_openai(text, is_wakeword):
                yield chunk

        else:
            # Try fallback TTS options
            fallback_order = [
                ("openai", text_to_speech_with_pipelining_openai),
                ("elevenlabs", text_to_speech_with_pipelining_elevenlabs),
                ("espeak", text_to_speech_with_pipelining_espeak),
                ("piper", text_to_speech_with_pipelining_piper),
            ]

            for name, func in fallback_order:
                if func is not None:
                    queue_message(
                        f"WARNING: TTS '{ttsoption}' not available, falling back to '{name}'"
                    )
                    if name in ["openai", "elevenlabs", "minimax"]:
                        async for chunk in func(text, is_wakeword):
                            yield chunk
                    else:
                        async for chunk in func(text):
                            yield chunk
                    return

            queue_message(f"ERROR: No TTS backend available for '{ttsoption}'")

    except Exception as e:
        queue_message(f"ERROR: Text-to-speech generation failed: {e}")


def initialize_interrupt():
    stt_manager = get_stt_manager()
    interrupt_recognizer = None
    if VOSK_AVAILABLE and stt_manager:
        if not hasattr(stt_manager, "vosk_model") or not stt_manager.vosk_model:
            # Load Vosk model if not already loaded
            model_path = os.path.join(
                os.getcwd(), "..", "stt", stt_manager.config["STT"]["vosk_model"]
            )
            try:
                stt_manager.vosk_model = Model(model_path)
            except Exception as e:
                queue_message(f"ERROR: Failed to load Vosk model for interrupt: {e}")
                return
            interrupt_recognizer = KaldiRecognizer(
                stt_manager.vosk_model, stt_manager.SAMPLE_RATE
            )
        return interrupt_recognizer
    return None


def cancel_speaker_echo(mic_audio, speaker_audio):
    """Remove speaker echo from microphone using reference signal subtraction"""
    try:
        # Ensure same length
        min_len = min(len(mic_audio), len(speaker_audio))
        mic_audio = mic_audio[:min_len]
        speaker_audio = speaker_audio[:min_len]

        # Normalize speaker audio to prevent over-cancellation
        speaker_max = np.max(np.abs(speaker_audio))
        if speaker_max > 0:
            speaker_audio = (speaker_audio / speaker_max) * np.max(np.abs(mic_audio))

        # Simple echo cancellation: subtract scaled speaker audio from mic
        # Use correlation to find optimal scaling factor
        correlation = np.dot(mic_audio, speaker_audio) / (
            np.dot(speaker_audio, speaker_audio) + 1e-8
        )
        echo_estimate = correlation * speaker_audio

        # Subtract echo and clip to int16 range
        cancelled = mic_audio - echo_estimate * 0.9  # 0.9 factor for stability
        cancelled = np.clip(cancelled, -32768, 32767).astype(np.int16)

        return cancelled
    except Exception as e:
        queue_message(f"DEBUG: Echo cancellation failed: {e}")
        return mic_audio


def apply_vad_filtering(audio_chunk, stt_manager):
    """Use voice activity detection to filter out echo and non-speech"""
    detected_speech = False
    try:
        # Use the existing Silero VAD from STT manager
        # voice_activity_detection_main returns (is_silence, detected_speech, silent_frames)
        is_silence, _, _ = stt_manager.voice_activity_detection_main(
            audio_chunk, detected_speech, silent_frames=0
        )
        # Return True if speech detected (is_silence is False)
        return not is_silence
    except Exception as e:
        queue_message(f"DEBUG: VAD check failed: {e}")
        return False


def listen_for_stop(interrupt_event, reference_audio_queue=None):
    stt_manager = get_stt_manager()
    interrupt_recognizer = initialize_interrupt()
    if not interrupt_recognizer or not stt_manager:
        return
    try:
        with sd.InputStream(
            samplerate=stt_manager.SAMPLE_RATE, channels=1, dtype="int16"
        ) as stream:
            while not interrupt_event.is_set():
                data, _ = stream.read(
                    int(stt_manager.SAMPLE_RATE * 0.25)
                )  # 250ms chunks
                data_mono = data[:, 0] if data.ndim > 1 else data

                # Apply echo cancellation using reference signal
                if reference_audio_queue:
                    try:
                        # Get latest speaker audio for cancellation
                        speaker_chunk = None
                        while not reference_audio_queue.empty():
                            speaker_chunk = reference_audio_queue.get_nowait()

                        if speaker_chunk is not None:
                            # Cancel echo from mic input
                            data_mono = cancel_speaker_echo(data_mono, speaker_chunk)
                    except Exception as e:
                        queue_message(f"DEBUG: Could not apply echo cancellation: {e}")

                # Filter with VAD - only process if actual speech detected
                is_speech = apply_vad_filtering(data_mono, stt_manager)

                if is_speech:
                    # Only send voice activity to recognizer
                    if interrupt_recognizer.AcceptWaveform(data_mono.tobytes()):
                        result = json.loads(interrupt_recognizer.Result())
                        transcript = result.get("text", "").lower()

                        # Words that trigger interrupt
                        interrupt_words = [
                            "stop",
                            "cancel",
                            "abort",
                            "nevermind",
                            "wait",
                            "hold on",
                        ]
                        if any(word in transcript for word in interrupt_words):
                            queue_message(f"INFO: Interrupt detected - '{transcript}'")
                            interrupt_event.set()
                            break
    except Exception as e:
        queue_message(f"ERROR: Interrupt listening failed: {e}")


def start_tts_interrupt_listener(reference_audio_queue=None):
    interrupt_event = threading.Event()
    interrupt_thread = threading.Thread(
        target=listen_for_stop,
        args=(interrupt_event, reference_audio_queue),
        daemon=True,
    )
    interrupt_thread.start()
    return interrupt_event, interrupt_thread


async def play_audio_chunks(text, config, is_wakeword=False):
    audio_queue = asyncio.Queue(maxsize=3)
    synthesis_done = asyncio.Event()
    interrupt_event = asyncio.Event()
    reference_audio_queue = None

    if not is_wakeword:
        # Create queue for passing speaker audio to interrupt listener for echo cancellation
        reference_audio_queue = asyncio.Queue(maxsize=10)
        interrupt_event, interrupt_thread = start_tts_interrupt_listener(
            reference_audio_queue
        )

    async def synthesize_chunks():
        try:
            async for audio_chunk in generate_tts_audio(text, config, is_wakeword):
                if interrupt_event.is_set():
                    break
                await audio_queue.put(audio_chunk)
        except Exception as e:
            queue_message(f"ERROR: Synthesis failed: {e}")
        finally:
            synthesis_done.set()

    async def play_chunks():
        try:
            requests.get("http://127.0.0.1:5012/start_talking", timeout=1)
        except:
            pass

        while True:
            try:
                try:
                    audio_chunk = await asyncio.wait_for(audio_queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    if synthesis_done.is_set() and audio_queue.empty():
                        break
                    continue

                if interrupt_event.is_set():
                    break

                data, samplerate = sf.read(audio_chunk, dtype="float32")
                max_val = np.max(np.abs(data))
                if max_val > 0:
                    data = data / max_val

                gain = 1.5
                data = np.clip(data * gain, -1.0, 1.0)

                # Convert to int16 for echo cancellation reference
                speaker_int16 = (data * 32767).astype(np.int16)
                if reference_audio_queue and not is_wakeword:
                    try:
                        reference_audio_queue.put_nowait(speaker_int16)
                    except asyncio.QueueFull:
                        pass  # Drop oldest reference if queue is full

                sd.play(data, samplerate)
                while sd.get_stream().active:
                    if interrupt_event.is_set():
                        sd.stop()
                        break

            except Exception as e:
                queue_message(f"ERROR: Failed to play chunk: {e}")
                if synthesis_done.is_set() and audio_queue.empty():
                    break

        try:
            requests.get("http://127.0.0.1:5012/stop_talking", timeout=1)
        except:
            pass

    await asyncio.gather(synthesize_chunks(), play_chunks())

    # Stop the interrupt thread
    if not is_wakeword:
        interrupt_event.set()
        interrupt_thread.join(timeout=1)
