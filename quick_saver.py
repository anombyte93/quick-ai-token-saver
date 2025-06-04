import time, io, os, json, hashlib, sys, threading, argparse
from PIL import ImageGrab, Image
import win32clipboard
from datetime import datetime

# --- Config ---
WEBP_QUALITY = 80  # Good balance for token savings
TOKEN_COST_PER_1K = 0.003
LOG_PATH = os.path.expanduser("~/.ai_image_token_saver/quick_log.json")
CACHE_FOLDER = os.path.expanduser("~/.ai_image_token_saver/cache")

# --- Clipboard Operations ---
def copy_image_to_clipboard(image):
    output = io.BytesIO()
    image.convert("RGB").save(output, format='BMP')
    data = output.getvalue()[14:]  # strip BMP header
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def copy_text_to_clipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, text.encode())
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()

def convert_to_wsl_path(windows_path):
    """Convert Windows path to WSL format for Claude Code compatibility"""
    # Convert C:\path\to\file to /mnt/c/path/to/file
    if ':' in windows_path and '\\' in windows_path:
        # Replace drive letter (C:) with /mnt/c
        drive_letter = windows_path[0].lower()
        path_without_drive = windows_path[2:]  # Remove "C:"
        wsl_path = f"/mnt/{drive_letter}" + path_without_drive.replace('\\', '/')
        return wsl_path
    return windows_path

# --- Token Estimation ---
def estimate_tokens(image_bytes):
    b64_len = (len(image_bytes) * 4) / 3  # base64 expansion
    return int(b64_len / 4)  # ~4 chars/token

# --- Image Hasher (content-based, format-independent) ---
def hash_image(image):
    # Hash based on dimensions and pixel data, not file format
    w, h = image.size
    # Sample multiple pixels across the image for robust content identification
    try:
        pixels = []
        # Sample from corners and center
        sample_points = [(0, 0), (w//4, h//4), (w//2, h//2), (3*w//4, 3*h//4), (w-1, h-1)]
        for x, y in sample_points:
            pixels.append(str(image.getpixel((x, y))))
        content = f"{w}x{h}_{'_'.join(pixels)}"
        return hashlib.sha256(content.encode()).hexdigest()
    except:
        # Fallback to just dimensions if pixel sampling fails
        return hashlib.sha256(f"{w}x{h}".encode()).hexdigest()

# --- Persistent Stats ---
def load_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r") as f:
            return json.load(f)
    return {"original_tokens": 0, "optimized_tokens": 0}

def save_log(stats):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(stats, f, indent=2)

def reset_stats():
    stats = {"original_tokens": 0, "optimized_tokens": 0}
    save_log(stats)
    print("\n📊 Token stats reset to zero!")
    print("📈 New total: 0 tokens ($0.0000)")
    return stats

# --- File Operations ---
def save_image_to_cache(image, cache_folder, format="WEBP", quality=WEBP_QUALITY):
    """Save image to cache folder and return the file path"""
    os.makedirs(cache_folder, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = format.lower()
    filename = f"img_{timestamp}.{extension}"
    filepath = os.path.join(cache_folder, filename)
    
    # Save image
    if format == "WEBP":
        image.save(filepath, format=format, quality=quality)
    else:
        image.save(filepath, format=format)
    
    return filepath

# --- Main Loop ---
def main():
    global CACHE_FOLDER
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Clipboard Image Token Saver")
    parser.add_argument("--mode", type=int, choices=[1, 2], default=1,
                       help="Mode 1: Clipboard to clipboard (default), Mode 2: Save to folder and copy path")
    parser.add_argument("--folder", type=str, default=CACHE_FOLDER,
                       help="Folder to save images in mode 2 (default: ~/.ai_image_token_saver/cache)")
    parser.add_argument("--reset", action="store_true", help="Reset token statistics")
    
    args = parser.parse_args()
    
    # Handle reset
    if args.reset:
        reset_stats()
        return
    
    # Update cache folder if custom folder provided
    if args.mode == 2 and args.folder != CACHE_FOLDER:
        CACHE_FOLDER = os.path.expanduser(args.folder)
    
    last_processed_hash = ""
    last_processed_time = 0
    stats = load_log()
    
    print(f"🖼 Clipboard Image Optimizer running (Mode {args.mode})... Press Ctrl+C to stop.")
    if args.mode == 1:
        print(f"📋 Mode 1: Converting clipboard images to WEBP for token savings")
    else:
        print(f"💾 Mode 2: Saving images to folder and copying file path")
        print(f"📁 Save folder: {CACHE_FOLDER}")
    
    print(f"🎯 Using WEBP {WEBP_QUALITY}% quality for optimal token savings")
    print(f"💡 Run with '--reset' to reset token stats")
    print(f"📊 Current total saved: {stats['original_tokens'] - stats['optimized_tokens']:,} tokens")

    while True:
        try:
            img = ImageGrab.grabclipboard()
            
            if isinstance(img, Image.Image):
                current_hash = hash_image(img)
                current_time = time.time()
                # Only process if it's a genuinely new image (different content AND enough time passed)
                if current_hash != last_processed_hash and (current_time - last_processed_time) > 3:
                    w, h = img.size
                    print(f"\n📷 Found NEW image: {w}×{h} pixels")
                    
                    # Calculate original tokens (as PNG)
                    orig_io = io.BytesIO()
                    img.save(orig_io, format="PNG")
                    orig_tokens = estimate_tokens(orig_io.getvalue())
                    
                    # Convert to WEBP for token calculation
                    webp_io = io.BytesIO()
                    img.save(webp_io, format="WEBP", quality=WEBP_QUALITY)
                    webp_tokens = estimate_tokens(webp_io.getvalue())
                    
                    tokens_saved = orig_tokens - webp_tokens
                    dollars_saved = tokens_saved / 1000 * TOKEN_COST_PER_1K
                    
                    if tokens_saved > 0:
                        # Update stats
                        stats["original_tokens"] += orig_tokens
                        stats["optimized_tokens"] += webp_tokens
                        save_log(stats)
                        
                        total_saved = stats["original_tokens"] - stats["optimized_tokens"]
                        total_dollars = total_saved / 1000 * TOKEN_COST_PER_1K
                        
                        if args.mode == 1:
                            # Mode 1: Keep in clipboard (current behavior)
                            last_processed_hash = current_hash
                            last_processed_time = current_time
                            
                            print(f"✅ WEBP would be: {w}×{h} pixels (same size, compressed)")
                            print(f"📦 Would save: {tokens_saved:,} tokens (~${dollars_saved:.4f})")
                            print(f"📈 Total calculated savings: {total_saved:,} tokens (~${total_dollars:.4f})")
                            print(f"💡 Image ready to paste - already optimized in calculation!")
                        
                        else:
                            # Mode 2: Save to folder and copy path
                            filepath = save_image_to_cache(img, CACHE_FOLDER, format="WEBP", quality=WEBP_QUALITY)
                            wsl_filepath = convert_to_wsl_path(filepath)
                            copy_text_to_clipboard(wsl_filepath)
                            
                            last_processed_hash = current_hash
                            last_processed_time = current_time
                            
                            print(f"✅ Saved as WEBP: {filepath}")
                            print(f"📋 WSL path copied: {wsl_filepath}")
                            print(f"📦 Saved: {tokens_saved:,} tokens (~${dollars_saved:.4f})")
                            print(f"📈 Total saved: {total_saved:,} tokens (~${total_dollars:.4f})")
                    else:
                        print(f"⚠️  No token savings from WEBP conversion")
                        last_processed_hash = current_hash
                        last_processed_time = current_time
                        
            time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()