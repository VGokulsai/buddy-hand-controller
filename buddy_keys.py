"""Buddy desktop helper: turns a hand sign into a real keystroke on your PC.

The webcam page (index.html) sends  GET http://127.0.0.1:5001/cmd/<sign>
and this presses the key that actually does the thing. It only listens on
your own machine (127.0.0.1), never the network.

    py -3 -m pip install pyautogui     # one time
    py -3 buddy_keys.py                # leave running while you use Buddy
    py -3 buddy_keys.py --check        # self-test, presses no keys

Signs -> actions (edit ACTIONS to change them):
    fist   open YouTube Music in your browser
    peace  previous browser tab      (Ctrl+Shift+Tab)
    thumb  minimize everything        (Win+D, "show desktop")
    palm   handled in the page (focus timer); no OS action here
"""
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer


def open_music():
    webbrowser.open("https://music.youtube.com")


def hotkey(*keys):
    # imported here so --check needs no install
    import pyautogui
    pyautogui.hotkey(*keys)


# each action is (label spoken in the log, function that does it).
# want fist to open Spotify instead? change the function. that's your knob.
ACTIONS = {
    "fist":  ("open YouTube Music",  open_music),
    "peace": ("previous tab",        lambda: hotkey("ctrl", "shift", "tab")),
    "thumb": ("minimize everything", lambda: hotkey("winleft", "d")),
}


def run(sign):
    """Do the action for a sign. Returns its label, or None if the sign is
    unknown -- unknown must be a clean 'nothing happened', never a crash."""
    action = ACTIONS.get(sign)
    if action is None:
        return None
    label, fn = action
    fn()
    return label


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        sign = self.path.rsplit("/", 1)[-1]
        try:
            label = run(sign)
        except Exception as e:
            self._send(500, "error: %s" % e)
            return
        if label is None:
            self._send(404, "unknown sign: %s" % sign)
        else:
            print("  %-6s -> %s" % (sign, label))
            self._send(200, label)

    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")   # page runs on :8099
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *a):    # silence the default request spam
        pass


def check():
    """Routing works and never crashes -- verified without pressing any key."""
    global ACTIONS
    hits = []
    ACTIONS = {k: (v[0], (lambda h=k: hits.append(h))) for k, v in ACTIONS.items()}
    assert run("fist")  == "open YouTube Music"
    assert run("thumb") == "minimize everything"
    assert run("nope")  is None, "unknown sign must return None, not crash"
    assert hits == ["fist", "thumb"], hits
    print("  3 checks pass")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
        sys.exit(0)
    port = 5001
    print("Buddy helper listening on http://127.0.0.1:%d   (Ctrl+C to stop)" % port)
    print("Leave this window open. Do a sign at the webcam page and it presses the key.")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
