# Word-cloud fonts

Place licensed `.ttf` or `.otf` font files in the folder for the language they support.

The word-cloud generator checks this folder first. It looks for a language-specific filename such as:

```text
fonts/
  arabic/
    NotoNaskhArabic-Regular.ttf
  hebrew/
    NotoSansHebrew-Regular.ttf
  latin/
    Archivo-Regular.ttf
    Archivo-Bold.ttf
  russian/
    NotoSans-Regular.ttf
```

For each word cloud, the generator randomly chooses from the selected language folder for each word. Latin-script languages use the `latin` folder when they do not have their own folder. If no project font is available, the generator falls back to an installed Windows font.

Noto Sans language fonts are a good choice because they have broad Unicode coverage. Download fonts only from a source that permits your intended use, and keep the font license with the font files.