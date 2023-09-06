import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from urllib.parse import urlparse, parse_qs
import concurrent.futures

# Set up the summarization pipeline
summarizer = pipeline("summarization")

# Function to fetch video subtitles (cached)
@st.cache_data
def fetch_subtitles(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([item["text"] for item in transcript])
        return text
    except Exception as e:
        return None

# Streamlit UI
st.set_page_config(page_title="Segmented YouTube Video Summarizer", layout="wide")

# Header
st.title("Segmented YouTube Video Summarizer")
st.write("Summarize YouTube videos with ease!")

# Input box for YouTube video URL
video_url = st.text_input("Enter YouTube Video URL:", "")

# Summarize button
if st.button("Summarize"):
    if video_url:
        parsed_url = urlparse(video_url)
        if parsed_url.netloc == "www.youtube.com":
            video_id = parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.netloc == "youtu.be":
            video_id = parsed_url.path[1:]
        else:
            video_id = None

        if video_id:
            video_content = fetch_subtitles(video_id)
            if video_content:
                num_iters = (len(video_content) + 999) // 1000
                summarized_text = []

                def summarize_segment(segment):
                    summary = summarizer(segment, max_length=200, min_length=50, do_sample=False)
                    return summary[0]['summary_text']

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    summarized_text = list(executor.map(summarize_segment, [video_content[i:i + 1000] for i in range(0, len(video_content), 1000)]))

                # Display the summarized text segments
                st.subheader("Segmented Summarized Text:")
                for i, segment_summary in enumerate(summarized_text):
                    st.write(f"Segment {i + 1}:\n{segment_summary}")
            else:
                st.error("Failed to fetch video content.")
        else:
            st.warning("Invalid YouTube URL. Please check the format.")
    else:
        st.warning("Please enter a YouTube video URL.")

# Add styling (unchanged)
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: pink;
        color: black;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stTextInput>div>div>input {
        background-color: black;
    }
    .stTextInput>label {
        font-weight: bold;
        color: #333;
    }
    .stTextInput {
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
