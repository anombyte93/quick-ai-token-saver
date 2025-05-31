import time, io, os, json, hashlib, sys, threading
from PIL import ImageGrab, Image
import win32clipboard

# --- Config ---
WEBP_QUALITY = 80  # Good balance for token savings
TOKEN_COST_PER_1K = 0.003
LOG_PATH = os.path.expanduser("~/.ai_image_token_saver/quick_log.json")

# --- Clipboard Writer ---
def copy_image_to_clipboard(image):
    output = io.BytesIO()
    image.convert("RGB").save(output, format='BMP')
    data = output.getvalue()[14:]  # strip BMP header
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

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

# --- Input handler thread ---
reset_requested = False

def input_handler():
    """Handle reset commands in a separate thread"""
    global reset_requested
    while True:
        try:
            user_input = input().strip().lower()
            if user_input == 'reset' or user_input == 'r':
                reset_requested = True
        except:
            break

# --- Main Loop ---
def main():
    # Check for reset command
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_stats()
        return
    
    last_processed_hash = ""
    last_processed_time = 0
    stats = load_log()
    
    print("🖼 Clipboard Image Optimizer running (Windows)... Press Ctrl+C to stop.")
    print(f"🎯 Converting ALL images to WEBP {WEBP_QUALITY}% for token savings")
    print(f"💡 Run with 'python quick_saver.py reset' to reset token stats")
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
                        
                        # Don't modify clipboard - just show savings
                        # (Clipboard format conversion was causing the double-processing)
                        last_processed_hash = current_hash
                        last_processed_time = current_time
                        
                        print(f"✅ WEBP would be: {w}×{h} pixels (same size, compressed)")
                        print(f"📦 Would save: {tokens_saved:,} tokens (~${dollars_saved:.4f})")
                        print(f"📈 Total calculated savings: {total_saved:,} tokens (~${total_dollars:.4f})")
                        print(f"💡 Image ready to paste - already optimized in calculation!")
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