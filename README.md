# buddy-hand-controller

A webcam hand-sign controller. You hold a sign to the camera and your PC does something: open music, switch tabs, minimize everything. Two parts:

- **`index.html`** reads your hand in the browser with Google MediaPipe (21 landmarks per hand), classifies the sign, and speaks what it is doing.
- **`buddy_keys.py`** is a small local helper that presses the real keys. The page sends `GET http://127.0.0.1:5001/cmd/<sign>` and the helper runs the action.

The helper listens only on `127.0.0.1`, never the network.

## What it is not

- Not a trained model. Signs are decided by a fixed rule (which fingers are up), not machine learning.
- Not a full gesture vocabulary. Four signs only: palm, fist, peace, thumb.
- Not cloud vision. MediaPipe runs in your browser; the model downloads once from a CDN, then runs locally.
- The helper does not run in the browser. Desktop actions need `buddy_keys.py` running; without it, only the in-page focus timer (palm) works.

## The signs

| Sign | Test key | Action |
|------|----------|--------|
| palm ✋ | `1` | Start a 25-minute focus timer (in the page) |
| fist ✊ | `2` | Open YouTube Music |
| peace ✌️ | `3` | Previous browser tab (Ctrl+Shift+Tab) |
| thumb 👍 | `4` | Minimize everything (Win+D) |

`palm` is handled entirely in the page. `fist`, `peace`, and `thumb` are real keystrokes done by the helper. Change what a sign does by editing the `ACTIONS` map in `buddy_keys.py`. No camera handy? Press keys `1`-`4` to fake the four signs and test the whole path.

## Run it

```
py -3 -m pip install pyautogui     # one time, for the helper
py -3 buddy_keys.py                # leave running while you use Buddy
py -3 buddy_keys.py --check        # self-test, presses no keys
```

Then open `index.html` in a browser and click **Start camera**. A sign fires once per new detection, with a 1.2-second cooldown so a held hand does not repeat.

Both parts carry a self-check: `buddy_keys.py --check` runs three routing assertions without pressing a key, and the page runs a five-case classifier self-test in the browser console on load.

## Known limitation

The sign classifier is a plain finger-up rule with a fixed thumb margin; odd hand angles or partial views can read as no sign or the wrong one. Detection uses one hand at a time.
