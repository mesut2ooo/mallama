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
pip install mallama
mallama --host 0.0.0.0 --port 5000
```

Via AUR (Arch Linux)
```bash
yay -S mallama
# or
paru -S mallama
```

# Run as a service
```bash
systemctl --user enable mallama
systemctl --user start mallama
```

From source
```bash
git clone https://github.com/mesut2ooo/mallama
cd mallama
pip install -e .
mallama
```

Requirements

    Python 3.8+
    Ollama installed and running locally (http://localhost:11434)

Usage

    Make sure Ollama is running with at least one model pulled
    Start the web UI: mallama
    Open http://localhost:5000 in your browser
    Select a model and start chatting!

Configuration
The application stores conversations and uploads in ~/.mallama/


License
MIT
