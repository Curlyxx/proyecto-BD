import win32com.client

speaker = win32com.client.Dispatch("SAPI.SpVoice")
voices = speaker.GetVoices()

for i, voice in enumerate(voices):
    print(f"{i}: {voice.GetDescription()}")