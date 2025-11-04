#!/usr/bin/env python3
"""
Basic Calculator Program
Performs addition, subtraction, multiplication, and division on two numbers.
"""
import webbrowser
import subprocess
import time
import threading

def set_system_volume(volume_percent):
    """Set macOS system volume (0-100)."""
    try:
        volume = max(0, min(100, volume_percent))
        # Use osascript to set volume on macOS
        subprocess.run(['osascript', '-e', f'set volume output volume {volume}'], 
                      capture_output=True, check=False)
    except Exception:
        pass  # Silently fail if volume control doesn't work

def play_music_with_volume_control(url, song_name):
    """Play music with volume control: low for ads, loud for song."""
    print(f"Playing {song_name}... 🎵")
    
    # Set volume low for ads (10% volume)
    set_system_volume(10)
    print("Volume set low for advertisements...")
    
    # Open YouTube video
    webbrowser.open(url)
    
    # After 20 seconds, increase volume to 80%
    def increase_volume():
        time.sleep(20)
        set_system_volume(80)
        print("Volume increased for the song! 🔊")
    
    # Run volume increase in background thread
    threading.Thread(target=increase_volume, daemon=True).start()

def get_number(prompt):
    """Get a valid number from the user."""
    while True:
        try:
            num = float(input(prompt))
            return num
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def calculate():
    """Main calculator function."""
    print("=" * 50)
    print("Basic Calculator")
    print("=" * 50)
    
    # Get two numbers from user
    num1 = get_number("Enter the first number: ")
    num2 = get_number("Enter the second number: ")
    
    print("\n" + "=" * 50)
    print("Results:")
    print("=" * 50)
    
    # Format numbers to remove unnecessary decimals
    def format_number(num):
        """Format number to remove trailing zeros and unnecessary decimals."""
        if num == int(num):
            return int(num)
        else:
            # Format to reasonable precision (up to 6 decimal places) and remove trailing zeros
            formatted = f"{num:.6f}".rstrip('0').rstrip('.')
            return formatted
    
    # Addition
    addition_result = num1 + num2
    if addition_result > 10:
        emotion = "😊"
    elif addition_result < 10:
        emotion = "☹️"
    else:
        emotion = ""
    print(f"\nAddition: {format_number(num1)} + {format_number(num2)} = {format_number(addition_result)} {emotion}")
    
    # Subtraction
    subtraction_result = num1 - num2
    print(f"Subtraction: {format_number(num1)} - {format_number(num2)} = {format_number(subtraction_result)}")
    
    # Multiplication
    multiplication_result = num1 * num2
    print(f"Multiplication: {format_number(num1)} × {format_number(num2)} = {format_number(multiplication_result)}")
    # Play music based on multiplication result
    if multiplication_result > 20:
        play_music_with_volume_control("https://www.youtube.com/watch?v=VmL6H7qFSRE", 
                                       "The Wheels on the Bus")
    elif multiplication_result < 20:
        play_music_with_volume_control("https://www.youtube.com/watch?v=XqZsoesa55w", 
                                       "Baby Shark")
    
    # Division
    if num2 != 0:
        division_result = num1 / num2
        print(f"Division: {format_number(num1)} ÷ {format_number(num2)} = {format_number(division_result)}")
    else:
        print(f"Division: {format_number(num1)} ÷ {format_number(num2)} = Cannot divide by zero!")
    
    print("\n" + "=" * 50)

def main():
    """Main loop that runs the calculator until user says no."""
    while True:
        calculate()
        
        # Ask if user wants to continue
        while True:
            response = input("\nDo you want to calculate again? (yes/no): ").lower().strip()
            if response in ['no', 'n']:
                print("Thank you for using the calculator! Goodbye! 👋")
                return
            elif response in ['yes', 'y']:
                print()  # Add a blank line for spacing
                break
            else:
                print("Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()