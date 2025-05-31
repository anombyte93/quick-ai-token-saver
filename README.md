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

   ```bash
   python quick_saver.py
   ```

3. **Take screenshots or copy images** - the tool automatically shows potential savings

4. **Reset your stats anytime** by typing `reset` and pressing Enter

## Example output

```
📊 CURRENT TOTAL SAVED: 248,472 tokens ($0.7454)

📷 Found NEW image: 1920×1080 pixels
✅ WEBP would be: 1920×1080 pixels (same size, compressed)
📦 This image saves: 15,230 tokens (~$0.0457)
📈 TOTAL SAVED: 263,702 tokens ($0.7911)
```

## Commands

- **Start**: `python quick_saver.py`
- **Reset stats at startup**: `python quick_saver.py reset`
- **Reset while running**: Type `reset` + Enter
- **Stop**: Ctrl+C

That's it! Start seeing how much you could save on AI image costs.
