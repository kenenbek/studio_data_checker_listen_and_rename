import os

# --- ☢️ NUCLEAR PROXY FIX ☢️ ---
# We must delete these variables so Gradio doesn't try to send
# localhost traffic to your corporate proxy.
for key in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
    if key in os.environ:
        del os.environ[key]

# Force Python to look locally
os.environ["no_proxy"] = "localhost,127.0.0.1,::1"


import gradio as gr
import pandas as pd
import json
import base64  # <--- NEW IMPORT


# --- CONFIGURATION ---
AUDIO_FOLDER = "/mnt/d/mbank-audio/tts_recordings_cutted/12.09.2025/Айганыш/quest_tv_show_007/"
JSON_FILE = os.path.join(AUDIO_FOLDER, "data_tv_show_007.json")

# --- CSS ---
custom_css = """
.gradio-container { max-width: 98% !important; }
#dataset_table { height: 85vh !important; max_height: 85vh !important; }
#dataset_table > .wrap { height: 100% !important; max_height: 100% !important; }
#dataset_table .tbody-wrap { max-height: 100% !important; height: 100% !important; }
audio { width: 100%; min-width: 200px; }
"""

def get_audio_html(file_path):
    """
    Reads the audio file as bytes and converts it to a Base64 HTML string.
    This ensures the browser can play it without needing to fetch a URL.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64_data = base64.b64encode(data).decode('utf-8')
            # Assuming .wav files. Change 'audio/wav' to 'audio/mp3' if needed.
            return f'<audio controls src="data:audio/wav;base64,{b64_data}"></audio>'
    except Exception as e:
        return f"Error loading audio: {e}"

def load_dataset():
    data_list = []

    if not os.path.exists(JSON_FILE):
        return pd.DataFrame({"Error": [f"JSON file not found"]})

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    for entry in json_data:
        filename = entry.get("audio")
        text = entry.get("pronounced_text")
        speaker = entry.get("speaker", "Unknown")
        tone = entry.get("tone", "Unknown")

        # Fix filename logic
        filename = filename.replace("quest_tv_show", "tv_show")
        full_audio_path = os.path.join(AUDIO_FOLDER, filename)

        if os.path.exists(full_audio_path):
            # --- THE FIX: USE BASE64 EMBEDDING ---
            audio_html = get_audio_html(full_audio_path)

            data_list.append({
                "Audio": audio_html,
                "Transcription": text,
                "Speaker": speaker,
                "Tone": tone,
                "Filename": filename
            })

    df = pd.DataFrame(data_list)
    if not df.empty:
        df = df[["Audio", "Transcription", "Speaker", "Tone", "Filename"]]

    return df

# --- UI ---
with gr.Blocks(title="TTS Reviewer", fill_height=True) as demo:
    gr.Markdown("## 🎧 TTS Dataset Reviewer")

    df = load_dataset()

    if not df.empty and "Audio" in df.columns:
        gr.DataFrame(
            value=df,
            datatype=["html", "str", "str", "str", "str"],
            headers=["Audio", "Transcription", "Speaker", "Tone", "Filename"],
            interactive=False,
            wrap=True,
            elem_id="dataset_table"
        )
    else:
        gr.Warning("No data found!")

# --- LAUNCH ---
if __name__ == "__main__":
    # We don't need allowed_paths anymore because we are embedding the data directly!
    demo.launch(
        server_port=9000,
        share=False,  # <--- This ensures NO public link is created
        theme=gr.themes.Soft(),
        css=custom_css
    )