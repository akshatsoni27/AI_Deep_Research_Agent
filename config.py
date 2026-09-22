"""Configuration shared by local runs and Streamlit Cloud."""

import os

from dotenv import load_dotenv

load_dotenv()


def get_setting(name: str, default: str | None = None) -> str | None:
    """Read a setting from the environment, then Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        value = st.secrets.get(name)
    except (ImportError, KeyError, FileNotFoundError):
        value = None

    return value or default