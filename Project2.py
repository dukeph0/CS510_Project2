"""
Class:   CS-510
Author:  Duke Pham
Date:    20 October 2025

Description:  This program is a multi-page, interactive Terminal User Interface (TUI) built
              using the curses and psutil libraries. It displays real-time system diagnositcs
              (CPU, Memory, Disk Usage) and includes separate pages to demonstrate multi-threading
              and error handling concepts
"""

"""
References:
- https://docs.python.org/3/howto/curses.html
- https://psutil.readthedocs.io/en/latest/
- https://docs.python.org/3/library/os.html
- https://docs.python.org/3/library/threading.html
"""

import os
import time
import psutil  # requires pip install
import sys
import threading
import curses

"""
  Provided Utility functions
"""

def printMsg1(num):
    time.sleep(0.01)  # Small delay to ensure both threads run
    threadLog.append(f"Thread 1 (Cubed): {num * num * num}")


def printMsg2(num):
    time.sleep(0.01)
    threadLog.append(f"Thread 2 (Squared): {num * num}")


# Configuration and State
quitKey = ord("q")
toggleKey = ord("t")
resizeCheckInterval = 0.5
minWidth = 80
minHeight = 21
pageCount = 5
currentPage = 0
threadLog = []


# Convert bytes to Gigabytes
def bytesToGb(bytesVal):
    return round(bytesVal / (1024**3), 2) if bytesVal else 0.0

# Helper function to draw a curses-based horizontal progress bar
def drawBar(win, y, x, percent, length=30, fullChar="|"):
    fillLength = int(length * percent / 100)
    bar = fullChar * fillLength + " " * (length - fillLength)
    win.addstr(y, x, f"[{bar}] {percent:.1f}%")

# Generates the entire colored/highlighted header bar for terminal navigation
def getTitle(pageNumber, currentWidth):
    # Mapping the page index to a display number (1-based)
    pageMap = {
        0: "1: CPU Statistics",
        1: "2: Memory Statistics",
        2: "3: Disk Usage Statistics",
        3: "4: Threading Demo",
        4: "5: Error Handling Demo",
    }

    # Get the title for the current page (used for highlighting)
    title = pageMap.get(pageNumber, "BLANK")

    # Create the full header line, listing all options
    fullHeader = ""
    for i in range(pageCount):
        # Determine if this option is the currently active one
        isActive = i == pageNumber

        # Add the page map string, highlighting the active page
        headerText = pageMap[i]

        if isActive:
            # Add reverse video attribute for the active page in the header
            fullHeader += f"| [ {headerText} ] "
        else:
            fullHeader += f"| {headerText} "

    fullHeader += "|"

    # Center the full header 
    return fullHeader


"""
   This function will display information about a file, size and file information.
   You can provide your own or use the projecttwo.txt file.

   Use psutil to get initial file information.
"""


def getFileDiskUsageStatistics(win, currentHeight, currentWidth) -> None:
    # print("Getting Disk Statistics")
    file_name = "./projecttwo.txt"
    yStart = 3

    win.addstr(
        yStart,
        2,
        "--- Specific File Information ---",
        curses.A_BOLD | curses.A_UNDERLINE,
    )

    if os.path.exists(file_name):
        try:
            # Use os.stat to get file system status (size, times, etc.)
            fileStats = os.stat(file_name)

            # Display file size (converting bytes to KB for readability)
            fileSizeKb = round(fileStats.st_size / 1024, 2)
            win.addstr(yStart + 2, 2, f"File Name: {file_name}")
            win.addstr(yStart + 3, 2, f"Size: {fileSizeKb:.2f} KB")

            # Display last modification time
            modifiedTime = time.ctime(fileStats.st_mtime)
            win.addstr(yStart + 4, 2, f"Last Modified: {modifiedTime}")

            # Advance the starting Y position for the next section
            yStart += 6

        except Exception as e:
            win.addstr(yStart + 2, 2, f"Error reading file stats: {e}")
            yStart += 4
    else:
        win.addstr(yStart + 2, 2, f"File Not Found: {file_name}", curses.color_pair(1))
        win.addstr(yStart + 3, 2, "Please create a file named 'projecttwo.txt'.")
        yStart += 5

    # Disk Stats (Focus on main partition)
    path = "/" if os.name != "nt" else "C:\\"
    disk = psutil.disk_usage(path)

    win.addstr(
        yStart,
        2,
        "--- Main Disk Partition Usage ---",
        curses.A_BOLD | curses.A_UNDERLINE,
    )
    win.addstr(yStart + 1, 2, f"Mount Point: {path}", curses.A_BOLD)
    win.addstr(yStart + 2, 2, "Total:")
    win.addstr(yStart + 2, 10, f"{bytesToGb(disk.total):.2f} GB")
    win.addstr(yStart + 3, 2, "Usage:")
    drawBar(win, yStart + 3, 10, disk.percent)


"""
   This should use psutil to retrieve standard and 
   virtual memory statistics
"""


def getMemoryStatistics(win, currentHeight, currentWidth) -> None:
    
    # Get detailed virtual memory statistics
    mem = psutil.virtual_memory()

    win.addstr(3, 2, "Virtual Memory Statistics:", curses.A_BOLD)
    
    # Calculate Total Memory
    total_gb = bytesToGb(mem.total)
    win.addstr(4, 2, "Total Memory:")
    win.addstr(4, 18, f"{total_gb:.2f} GB")

    # Calculate Used Memory
    used_gb = bytesToGb(mem.used)
    win.addstr(5, 2, "Used Memory:")
    win.addstr(5, 18, f"{used_gb:.2f} GB")

    # Calculate Available Memory
    available_gb = bytesToGb(mem.available)
    win.addstr(6, 2, "Available:")
    win.addstr(6, 18, f"{available_gb:.2f} GB")

    # 4. Overall Usage Percentage (with bar)
    usage_percent = mem.percent
    win.addstr(8, 2, "Usage Percentage:")
    drawBar(win, 8, 18, usage_percent) 


"""
   This should use psutil to retrieve CPU statistics, including
   information on processes.
"""


def getCpuStatistics(win, currentHeight, currentWidth) -> None:
   
    # Get overall CPU usage percentage and the total number of logical cores
    cpuPercent = psutil.cpu_percent(interval=0.5)
    cpuCores = psutil.cpu_count(logical=True)

    # Display the total logical core count and the overall CPU usage bar
    win.addstr(3, 2, f"Total CPU Cores (Logical): {cpuCores}", curses.A_BOLD)
    win.addstr(4, 2, "Overall Usage:")
    drawBar(win, 4, 18, cpuPercent)

    # Per-core usage (display max 8 cores for simple layout)
    perCpu = psutil.cpu_percent(interval=0.5, percpu=True)
    win.addstr(6, 2, "Per-Core Usage:", curses.A_UNDERLINE)
    for i, p in enumerate(perCpu[:8]):
        win.addstr(7 + i, 2, f"Core {i}:")
        drawBar(win, 7 + i, 12, p, length=20)


    startY = 7 + min(len(perCpu), 8) + 2  # Calculate start position below core usage

    win.addstr(startY, 2, "Top 5 CPU Processes:", curses.A_BOLD | curses.A_UNDERLINE)

    # Get all processes and sort them by CPU usage
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        processes.append(proc.info)

    # Filter out processes that haven't registered CPU time yet (0.0)
    # Sort by 'cpu_percent' in descending order
    # Take the top 5
    topProcesses = sorted(
        [
            p
            for p in processes
            if p["cpu_percent"] is not None and p["cpu_percent"] > 0.0
        ],
        key=lambda p: p["cpu_percent"],
        reverse=True,
    )[:5]

    # Display the top 5 processes
    win.addstr(startY + 1, 2, f"{'PID':<6} {'CPU %':<8} {'Name'}")

    for i, p in enumerate(topProcesses):
        y = startY + 2 + i
        if y < currentHeight - 1:  # Boundary check
            name = p["name"][: currentWidth - 25]  # Truncate name to fit screen
            win.addstr(y, 2, f"{p['pid']:<6} {p['cpu_percent']:<8.1f} {name}")


"""
   This function will show multi threading capabilities.

   Two threads should be created.
    
   One used to call the function "printMsg1" provided above.

   A second thread should call the function "printMsg2" provided above.
"""


def showThreadingExample(win, currentHeight, currentWidth) -> None:
    # Start timer
    startTime = time.perf_counter()
 
    # Declare 'threadLog' as a global variable to modify the list defined outside this function
    global threadLog

    win.addstr(3, 2, "Threading Demonstration:", curses.A_BOLD)

    # Only run threads once
    if not threadLog:
        thread1 = threading.Thread(target=printMsg1, args=(5,))
        thread2 = threading.Thread(target=printMsg2, args=(10,))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    # Base row for the log messages is 4
    log_start_row = 4
    for i, msg in enumerate(threadLog):
        # Add log messages, performing a boundary check
        if log_start_row + i < currentHeight - 1:
            win.addstr(log_start_row + i, 2, msg)

    # Calculate the row immediately following the last log message
    done_message_row = log_start_row + len(threadLog)

    # Print the "Done With Threading!" message using curses
    if done_message_row < currentHeight - 1:
        win.addstr(done_message_row, 2, "Done With Threading!", curses.A_BOLD)

    # Stop timer and calculate elapsed time
    endTime = time.perf_counter()
    elapsedTime = (endTime - startTime) * 1000  # Convert to milliseconds

    # Determine the row to print the timing result 
    timing_row = done_message_row + 2
    
    # Display the timing result to the curses window
    if timing_row < currentHeight - 1:
        timing_message = f"Execution Time (w/ Join): {elapsedTime:.3f} ms"
        win.addstr(timing_row, 2, timing_message)

    explanation_row = timing_row + 1
    if explanation_row < currentHeight - 1:
        win.addstr(explanation_row, 2, "(NOTE: Time updates on every screen refresh.)")


"""
   This function shows system error handling.

   Since out of memory, or out of disk space errors are difficult to create,
   we will use a divide by zero error and show the error handling being executed.
"""


def showErrorHandling(win, currentHeight, currentWidth) -> None:
    # Start timer
    startTime = time.perf_counter()
   
    # Display function title
    win.addstr(3, 2, "Error Handling Demonstration:", curses.A_BOLD)

    try:
        # Causing a divide by zero error
        result = 100 / 0
        win.addstr(5, 2, f"Result is {result}")

    except ZeroDivisionError:
        win.addstr(
            5, 2, "ZeroDivisionError caught:", curses.color_pair(1) | curses.A_BOLD
        )
        win.addstr(6, 2, "You can't divide by zero!")

    except Exception as e:
        win.addstr(5, 2, f"Other Error: {e}")

    finally:
        win.addstr(8, 2, "Execution complete.", curses.A_BOLD)

        # Stop timer and calculate elapsed time
        endTime = time.perf_counter()
        elapsedTime = (endTime - startTime) * 1000 # Convert to millseconds

        # Display the timing result in the curses window
        timingMessage = f"Execution Time: {elapsedTime:.3f} ms"
        win.addstr(10, 2, timingMessage)

        win.addstr(11, 2, "(NOTE: Time updates on every screen refresh.)")

# Function map for five page applications 
PAGES = [
    getCpuStatistics,
    getMemoryStatistics,
    getFileDiskUsageStatistics,
    showThreadingExample,
    showErrorHandling,
]

# User Interface Setup
def cursesApp(stdscr):
    # Declare 'currentPage' as a global variable to modify the list defined outside this function
    global currentPage

    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Color error handling
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)  # for errors

    # Resize variables
    lastSizeHeight, lastSizeWidth = stdscr.getmaxyx()
    lastTime = time.time()

    while True:
        # Get current dimensions
        currentHeight, currentWidth = stdscr.getmaxyx()

        # Handle resizing
        if currentHeight != lastSizeHeight or currentWidth != lastSizeWidth:
            # Clear and redraw
            stdscr.erase()
            lastSizeHeight, lastSizeWidth = currentHeight, currentWidth
            curses.resizeterm(currentHeight, currentWidth)

        # Check when terminal is too small
        if currentWidth < minWidth or currentHeight < minHeight:
            stdscr.erase()
            stdscr.addstr(
                currentHeight // 2,
                currentWidth // 2 - 20,
                f"RESIZE: Terminal must be at least {minWidth}x{minHeight}",
            )
            stdscr.refresh()
            time.sleep(0.1)
            continue

        # Draw User Interface
        stdscr.erase()
        stdscr.border(0)

        # Header
        stdscr.addstr(0, 0, getTitle(currentPage, currentWidth), curses.A_REVERSE)

        # Content Area
        PAGES[currentPage](stdscr, currentHeight, currentWidth)

        # Footer
        stdscr.addstr(
            currentHeight - 1,
            2,
            f" Click through 1-5 for different options | Press 'q' to QUIT | Screen: {currentWidth}X{currentHeight} ",
        )

        stdscr.refresh()

        # Handle Input
        key = stdscr.getch()
        if key != -1:  # Check if a key was pressed
            if key == quitKey:
                break

            # Check for keys '1' through '5'
            if ord("1") <= key <= ord("5"):
                # Convert the ASCII character code (e.g., ord('3')) to the integer value (3)
                # Subtract 1 to get the 0-based index (e.g., 3 - 1 = index 2)
                newPageIndex = key - ord("1")

                # Check if the calculated index is within the defined pageCount
                if 0 <= newPageIndex < pageCount:
                    currentPage = newPageIndex

        time.sleep(0.1)


"""
   Main function
"""

# Print a nice welcome banner
def displayStartupBanner():
    """Prints a non-curses banner before starting the TUI application."""
    print("=" * 60)
    print("━┏┛┏━┛┏━┛┃ ┃┏━┛┏━┛┏━┛┃ ┃┏━┃┏━┛  ┏━┛┏━┃┃  ┃ ┃━┏┛┛┏━┃┏━ ┏━┛")
    print(" ┃ ┏━┛┃  ┏━┃━━┃┏━┛┃  ┃ ┃┏┏┛┏━┛  ━━┃┃ ┃┃  ┃ ┃ ┃ ┃┃ ┃┃ ┃━━┃")
    print(" ┛ ━━┛━━┛┛ ┛━━┛━━┛━━┛━━┛┛ ┛━━┛  ━━┛━━┛━━┛━━┛ ┛ ┛━━┛┛ ┛━━┛")
    print(" SNHU CS510: System Optimization Benchmarker")
    print("=" * 60)
    print("\nStarting application... Press Enter to continue.")

    # Wait for the user to acknowledge the banner
    input()

# Have Fancy User Interface in main
if __name__ == "__main__":

    displayStartupBanner()

    # Launch the curses app, handling errors like terminal failures or user interruption (Ctrl+C)
    try:
        curses.wrapper(cursesApp)
    except curses.error:
        print(
            "\nTerminal initializtion failed. Ensure your terminal supports curses and is sized appropriately"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram Terminated")
        sys.exit(0)
