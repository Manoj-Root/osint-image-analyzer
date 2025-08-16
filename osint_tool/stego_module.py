# osint_tool/stego_module.py
import os
import platform
import subprocess

def _run(cmd, shell=False):
    return subprocess.run(cmd, shell=shell, capture_output=True, text=True)

def _combined_output(proc):
    return ((proc.stdout or "") + "\n" + (proc.stderr or "")).lower()

def _steghide_extract(image_path, password, outfile):
    """
    Try extracting with steghide using a specific password.
    Returns (success: bool, message: str)
    """
    # Remove old outfile so we can trust file existence as a success signal
    try:
        if os.path.exists(outfile):
            os.remove(outfile)
    except Exception:
        pass

    proc = _run([
        "steghide", "extract",
        "-sf", image_path,
        "-p", password,
        "-xf", outfile,
        "-f"  # force overwrite silently
    ])

    combined = _combined_output(proc)
    # Strongest signal: file was actually created and has content
    if os.path.exists(outfile) and os.path.getsize(outfile) > 0:
        return True, "extracted (outfile present)"
    # Fallback textual signal (stdout/stderr varies across builds)
    if "wrote extracted data" in combined or "extracting data" in combined:
        return True, "extracted (text signal)"
    return False, combined.strip()

def check_stego(file_path, password=None, wordlist=None, outfile="output.bin"):
    print(f"\n🔍 Steganography Analysis for {file_path}")

    is_windows = platform.system().lower() == "windows"

    # 1) strings (quick peek)
    print("\n[+] Checking for printable strings (first 20 lines):")
    try:
        res = _run(["strings", file_path])
        lines = (res.stdout or "").splitlines()
        print("\n".join(lines[:20]) if lines else "No strings found.")
    except Exception as e:
        print(f"strings error: {e}")

    # 2) header hints via grep/findstr
    print("\n[+] Scanning for embedded headers (JFIF/EXIF/PNG/ID3/PK):")
    try:
        if is_windows:
            cmd = f"strings {file_path} | findstr /i \"JFIF EXIF PNG ID3 PK\""
        else:
            cmd = f"strings {file_path} | grep -iE 'JFIF|EXIF|PNG|ID3|PK'"
        res = _run(cmd, shell=True)
        out = res.stdout if res.stdout else res.stderr
        print(out.strip() or "No embedded headers found.")
    except Exception as e:
        print(f"header scan error: {e}")

    # 3) binwalk
    print("\n[+] Running binwalk:")
    try:
        res = _run(["binwalk", file_path])
        print((res.stdout or res.stderr or "").strip() or "No signatures found.")
    except Exception as e:
        print(f"binwalk error: {e}")

    # 4) zsteg (PNG only, Linux/mac)
    if file_path.lower().endswith(".png") and not is_windows:
        print("\n[+] Running zsteg (PNG LSB analysis):")
        try:
            res = _run(["zsteg", file_path])
            print((res.stdout or res.stderr or "").strip() or "No hidden data found by zsteg.")
        except FileNotFoundError:
            print("zsteg not installed; skipping.")
        except Exception as e:
            print(f"zsteg error: {e}")

    # 5) steghide extraction (JPG/JPEG/BMP/WAV/AU only)
    if not file_path.lower().endswith((".jpg", ".jpeg", ".bmp", ".wav", ".au")):
        print("\nℹ️ steghide not attempted (unsupported format). Use JPG/JPEG/BMP/WAV/AU.")
        print("\n[✔] Stego analysis complete.")
        return

    print(f"\n[+] Steghide extraction to: {outfile}")

    # a) Direct password
    if password:
        ok, msg = _steghide_extract(file_path, password, outfile)
        if ok:
            print(f"✅ Extracted with provided password: {password}")
            print(f"📄 Saved: {outfile}")
            print("\n[✔] Stego analysis complete.")
            return
        else:
            print(f"❌ Password failed. Detail: {msg}")

    # b) Wordlist brute force
    if (not password) and wordlist:
        if not os.path.exists(wordlist):
            print(f"❌ Wordlist not found: {wordlist}")
            print("\n[✔] Stego analysis complete.")
            return

        print(f"🔑 Brute forcing with wordlist: {wordlist}")
        tried = 0
        try:
            with open(wordlist, "r", encoding="latin-1", errors="ignore") as f:
                for line in f:
                    pw = line.strip()
                    if not pw:
                        continue
                    tried += 1
                    ok, msg = _steghide_extract(file_path, pw, outfile)
                    if ok:
                        print(f"✅ Password found: {pw}")
                        print(f"📄 Saved: {outfile}")
                        print("\n[✔] Stego analysis complete.")
                        return
                    # Print a heartbeat occasionally so long lists don't look stuck
                    if tried % 500 == 0:
                        print(f"…tried {tried} passwords")

            print(f"❌ No working password in wordlist (tried {tried}).")
        except Exception as e:
            print(f"bruteforce error: {e}")

    # c) Neither provided → try empty password as a last attempt
    if not password and not wordlist:
        ok, msg = _steghide_extract(file_path, "", outfile)
        if ok:
            print("✅ Extracted with empty password")
            print(f"📄 Saved: {outfile}")
        else:
            print("ℹ️ No password/wordlist provided and empty password failed.")

    print("\n[✔] Stego analysis complete.")
