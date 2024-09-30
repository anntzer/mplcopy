"""
Copying Matplotlib figures
==========================

Register ctrl+c (cmd+c on macOS) as shortcut for copying the current figure to
the system clipboard.  On Linux, this depends on xclip_.

For Matplotlib 3.7 or higher, mplcopy can be registered by setting
``rcParams["figure.hooks"] = ["mplcopy:setup"]``.  In that case, mplcopy
will be automatically installed on any Figure the first time it is drawn.
Otherwise, explicitly call ``mplcopy.setup(figure)`` for each figure as
desired.

.. _xclip: https://github.com/astrand/xclip

-------------------------------------------------------------------------------

Copyright (c) 2023-present Antony Lee

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
"""


import functools
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

import matplotlib as mpl
import PIL


def setup(figure):
    """
    A hook function that can be registered into ``rcParams["figure.hooks"]``.
    """

    @functools.partial(figure.canvas.mpl_connect, "key_press_event")
    # Copy the figure as it appears on the screen, not as it would be saved.
    @mpl.rc_context({"savefig.transparent": False})
    def on_key_press(event):
        if sys.platform == "darwin":
            if event.key != "cmd+c":
                return
            with TemporaryDirectory() as tmpdir:
                figure.savefig(Path(tmpdir, "fig.tiff"))
                subprocess.run([
                    "osascript", "-e",
                    'set the clipboard to (read "fig.tiff" as TIFF picture)',
                ], cwd=tmpdir, check=True)
        elif sys.platform == "linux":
            if event.key != "ctrl+c":
                return
            if not shutil.which("xclip"):
                raise RuntimeError("On Linux, mplcopy depends on xclip")
            buf_png = BytesIO()
            figure.savefig(buf_png, format="png")
            subprocess.run([
                "xclip", "-sel", "clipboard", "-t", "image/png"
            ], input=buf_png.getvalue(), check=True)
        elif sys.platform == "win32":
            if event.key != "ctrl+c":
                return
            buf_png = BytesIO()
            buf_bmp = BytesIO()
            figure.savefig(buf_png, format="png")
            PIL.Image.open(buf_png).save(buf_bmp, format="bmp")
            import win32clipboard as wc
            wc.OpenClipboard()
            try:
                wc.EmptyClipboard()
                # Skip 14-byte BMP header before the DIB header.
                wc.SetClipboardData(wc.CF_DIB, buf_bmp.getvalue()[14:])
            finally:
                wc.CloseClipboard()
