# Ollama Web UI

A beautiful web interface for Ollama with conversation management and markdown support.

## Features

- 💬 Chat with Ollama models
- 📝 Markdown support with syntax highlighting
- 💾 Save and manage conversations
- ⚙️ Adjustable parameters (temperature, top-p, max tokens)
- 📎 File upload support
- 🎨 Beautiful glass-morphism UI
- ⌨️ Keyboard shortcuts (Ctrl+C to stop generation)

## Installation

### Via pip
```bash
pip install ollama-webui
ollama-webui --host 0.0.0.0 --port 5000

Via AUR (Arch Linux)
bash

yay -S ollama-webui
# or
paru -S ollama-webui

# Run as a service
systemctl --user enable ollama-webui
systemctl --user start ollama-webui

From source
bash

git clone https://github.com/yourusername/ollama-webui
cd ollama-webui
pip install -e .
ollama-webui

Requirements

    Python 3.8+

    Ollama installed and running locally (http://localhost:11434)

Usage

    Make sure Ollama is running with at least one model pulled

    Start the web UI: ollama-webui

    Open http://localhost:5000 in your browser

    Select a model and start chatting!

Configuration

The application stores conversations and uploads in ~/.ollama-webui/
License

MIT
text


### **tests/__init__.py**
```python
# Test package
