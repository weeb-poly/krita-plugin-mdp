# `neet`

This code is structured to match up to how FireAlpaca *might* structure everything.

Since FireAlpaca uses Qt, we're assuming

- Some variable / class names are from the [`mdp_format`](https://github.com/rsuzaki/mdp_format) docs
- Some variable / class names are based on external symbols from the macOS version
  ```
  nm -g /Applications/FireAlpaca.app/Contents/MacOS/FireAlpaca | grep neet
  ```
- Some variable / class names are completely made up based on whatever information I have

Krita currently only supports `PyQt5`. Qt for Python (`PySide6`) isn't supported, so we're currently defaulting to `PySide6` to support potential use cases outside of Krita.
