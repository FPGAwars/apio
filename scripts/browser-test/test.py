import webbrowser
from pathlib import Path

def open_in_browser(file_path):
    # Convert file path to a proper file:// URI
    file_uri = Path(file_path).resolve().as_uri()

    # Try Chrome first (Windows, macOS, Linux), then fall back to default browser
    #browser_options = [
    #    "chrome",                  # Windows
    #    "open -a 'Google Chrome'",# macOS
    #    "google-chrome",          # Linux
    #    "chromium-browser"        # Linux alternative
    #]

    #for option in browser_options:
    #    try:
    #        webbrowser.get(option).open(file_uri)
    #        return
    #    except webbrowser.Error:
    #        continue

    # Fallback — use system default browser
    webbrowser.open(file_uri)

if __name__ == "__main__":
    #open_in_browser("test.svg")
    #open_in_browser("test.pdf")
    open_in_browser("test.png")

