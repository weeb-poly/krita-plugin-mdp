# MDIPACK Import Plugin for Krita

***Warning:*** MDIPACK files are not fully supported and may result in significant data loss during the conversion process. See the Compatibility section for more info.

This plugin attempts to add support for importing MDIPACK files (`*.mdp`) to Krita.

The MDIPACK file format is used by applications such as mdiapp+, FireAlpaca, MediBang Paint, LayerPaint HD, and probably more.

This was based on a separate project to try and convert MDIPACK files to OpenRaster files, but this seemed like an easier solution.

Krita doesn't seem to allow implementing impex plugins in Python, so this plugin can only be accessed from "Tools -> Scripts" at this time.

The Python plugin relies on built-ins rather than using the Qt / C++ equivalents whenever possible.

## Compatibility

MDIPACK files are not fully supported and may result in significant data loss during the conversion process.

I recommend using the latest version of the app that created the MDP file to export a PSD file. If the app doesn't have the ability to export to PSD, try using the latest version of FireAlpaca. The PSD file should import into Krita with minimal issues.

If you encounter an issue, feel free to reach out with the following:

- Plugin Version (git hash)
- Krita Version
- MDP File
- Exported PSD File (Exported)
- App used to make MDP file (Name and Version)
- App used to make PSD file (Name and Version)

## Notes

mdiapp+ is developed by nattou.org and published by PGN Inc.
FireAlpaca is developed and published by PGN Inc.

This repo includes other packages in `site-packages`.

I believe this plugin is compliant under FireAlpaca's Terms of Service as of the time this is being published.

I would like to thank Um6ra1 for his notes on the file format and Bowserinator for translating said notes from Japanese to English.

I would like to thank 42aruaour for directing me to the nattou.org group, who created the spec as well as most of applications that use it.

Finally, I would like to thank rsuzaki for sharing a lot of information on the MDIPACK file format ([link](https://github.com/rsuzaki/mdp_format)). This information was extremely helpful in order to get this plugin to the state that it is.
