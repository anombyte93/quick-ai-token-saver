# 💰 Clipboard Image Token Saver

**Stop wasting money on huge image tokens when using AI!**

This tool automatically calculates how much you could save by optimizing images before pasting them into ChatGPT, Claude, or AI APIs.

## What it does

- Watches your clipboard for screenshots and images
- Calculates how many tokens the image costs in PNG vs optimized WEBP format
- Shows you potential savings in tokens and dollars
- Keeps a running total of how much you could save

## Why you need this

AI image tokens are **expensive**! A single large screenshot can cost:

- **Original PNG**: 25,000 tokens ($0.075)
- **Optimized WEBP**: 8,000 tokens ($0.024)
- **You save**: 17,000 tokens ($0.051) per image

If you use AI daily with images, this adds up to **hundreds of dollars** in savings.

## How to use

1. **Install requirements:**

   ```bash
   pip install Pillow pywin32
   ```

2. **Run the script:**

   **Mode 1 (Clipboard to Clipboard)** - Default mode, shows savings without modifying clipboard:
   ```bash
   python quick_saver.py
   ```

   **Mode 2 (Save to Folder)** - Saves optimized images and copies file path to clipboard:
   ```bash
   python quick_saver.py --mode 2
   ```

   With custom folder:
   ```bash
   python quick_saver.py --mode 2 --folder "C:/my_images"
   ```

3. **Take screenshots or copy images**:
   - Mode 1: Shows potential savings, keeps original in clipboard
   - Mode 2: Saves optimized WEBP to folder, copies file path to clipboard for pasting into Claude Code

4. **Reset your stats anytime** with `--reset` flag

## Example output

```
📊 CURRENT TOTAL SAVED: 248,472 tokens ($0.7454)

📷 Found NEW image: 1920×1080 pixels
✅ WEBP would be: 1920×1080 pixels (same size, compressed)
📦 This image saves: 15,230 tokens (~$0.0457)
📈 TOTAL SAVED: 263,702 tokens ($0.7911)
```

## Commands

- **Mode 1 (default)**: `python quick_saver.py`
- **Mode 2 (save & copy path)**: `python quick_saver.py --mode 2`
- **Custom save folder**: `python quick_saver.py --mode 2 --folder "C:/my_folder"`
- **Reset stats**: `python quick_saver.py --reset`
- **Stop**: Ctrl+C

## Mode Details

**Mode 1**: Best for direct AI chat interfaces where you paste images
- Keeps original image in clipboard
- Shows token savings calculations only

**Mode 2**: Perfect for Claude Code and file-based AI tools
- Saves optimized WEBP to disk
- Automatically converts Windows paths to WSL format
- Copies WSL-compatible file path to clipboard
- You paste the path into Claude Code to share the image

That's it! Start seeing how much you could save on AI image costs.
