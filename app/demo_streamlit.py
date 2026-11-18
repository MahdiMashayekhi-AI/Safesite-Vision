"""Streamlit demo for SafeSite Vision.

Run locally:
    uv run streamlit run app/demo_streamlit.py

TODO(phase-5): accept an uploaded video, run the pipeline and render
per-track compliance state plus the violation event feed.
"""

from __future__ import annotations

import streamlit as st


def main() -> None:
    """Render the demo page."""
    st.set_page_config(page_title="SafeSite Vision", page_icon="🦺", layout="wide")
    st.title("SafeSite Vision")
    st.caption("Real-time PPE detection and safety-compliance demo")

    st.info(
        "Scaffold only: the interactive pipeline is implemented in Phase 5. "
        "See the roadmap for the current status."
    )

    with st.sidebar:
        st.header("Configuration")
        st.text_input("Weights", value="models/ppe_yolo.pt", disabled=True)
        st.slider("Confidence threshold", 0.0, 1.0, 0.25, disabled=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Detections")
        st.write("No video source selected.")
    with col_right:
        st.subheader("Violation events")
        st.write("No events yet.")


if __name__ == "__main__":  # pragma: no cover - manual invocation only
    main()
