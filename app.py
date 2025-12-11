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
html, body { 
    margin: 0 !important; 
    padding: 0 !important; 
    height: 100vh !important; 
    overflow: hidden !important;
}
.gradio-container { 
    max-width: 100% !important; 
    padding: 5px !important;
    margin: 0 !important;
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
}
.main { 
    height: 100% !important; 
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
.contain { 
    height: 100% !important; 
    display: flex !important;
    flex-direction: column !important;
}
.block {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}
#dataset_table { 
    flex: 1 !important;
    height: 100% !important; 
    min-height: 0 !important;
    max-height: none !important;
}
#dataset_table > div {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}
#dataset_table .wrap { 
    height: 100% !important;
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}
#dataset_table .table-wrap {
    flex: 1 !important;
    height: 100% !important;
    max-height: none !important;
    overflow: auto !important;
}
#dataset_table table {
    height: 100% !important;
}
#dataset_table thead {
    position: sticky !important;
    top: 0 !important;
    background: white !important;
    z-index: 10 !important;
}
#dataset_table .tbody-wrap { 
    max-height: none !important; 
    height: 100% !important;
    flex: 1 !important;
}
#dataset_table tbody {
    height: 100% !important;
}
/* Target all parent divs */
#dataset_table,
#dataset_table > *,
#dataset_table > * > * {
    display: flex !important;
    flex-direction: column !important;
}
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
    gr.Markdown("### 🎧 TTS Dataset Reviewer")

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
        server_name="127.0.0.1",  # <--- Explicitly bind to localhost
        server_port=9000,
        share=False,  # <--- This ensures NO public link is created
        theme=gr.themes.Soft(),
        css=custom_css
    )