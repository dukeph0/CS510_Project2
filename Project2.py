"""
Class:   CS-510
Author:  Duke Pham
Date:    20 October 2025

Description:  Each function that needs to be completed has a comment at the top with
              TODO written in it with instructions.

              Within the function is a section with the comment #TODO where you will
              insert your code as per the instructions.
"""

import os
import time
import psutil  # requires pip install
import sys
import threading
import curses

"""
  Three provided Utility functions to use
"""
# def printBlankLines(lines: int):
#     for i in range(lines):
#         print("")

threadLog = []

# def printMsg1(num):
#     print("Thread 1 cubed: {}" .format(num * num * num))


# def printMsg2(num):
#     print("Thread 2 squared: {}" .format(num * num))


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


# Convert bytes to Gigabytes
def bytesToGb(bytesVal):
    return round(bytesVal / (1024**3), 2) if bytesVal else 0.0


def drawBar(win, y, x, percent, length=30, fullChar="#"):
    fillLength = int(length * percent / 100)
    bar = fullChar * fillLength + " " * (length - fillLength)
    win.addstr(y, x, f"[{bar}] {percent:.1f}%")


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
        is_active = i == pageNumber

        # Add the page map string, highlighting the active page
        header_text = pageMap[i]

        if is_active:
            # Add reverse video attribute for the active page in the header
            fullHeader += f"| [ {header_text} ] "
        else:
            fullHeader += f"| {header_text} "

    fullHeader += "|"

    # Center the full header 
    return fullHeader


"""
   TODO This function will display information about a file, size and file information.
   You can provide your own or use the projecttwo.txt file.

   Use psutil to get initial file information.
"""


def getFileDiskUsageStatistics(win, currentHeight, currentWidth) -> None:
    # print("Getting Disk Statistics")
    file_name = "./projecttwo.txt"
    yStart = 3

    # TODO INSERT YOUR CODE HERE
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
   TODO This should use psutil to retrieve standard and 
   virtual memory statistics
"""


def getMemoryStatistics(win, currentHeight, currentWidth) -> None:
    # print("Getting Memory Statistics")

    # TODO INSERT YOUR CODE HERE

    # Memory Stats
    mem = psutil.virtual_memory()
    win.addstr(3, 2, "Virtual Memory Statistics:", curses.A_BOLD)
    win.addstr(4, 2, "Total:")
    win.addstr(4, 10, f"{bytesToGb(mem.total):.2f} GB")
    win.addstr(5, 2, "Usage:")
    drawBar(win, 5, 10, mem.percent)


"""
   TODO This should use psutil to retrieve CPU statistics, including
   information on processes.
"""


def getCpuStatistics(win, currentHeight, currentWidth) -> None:
    # print("Getting CPU Statistics")

    # TODO INSERT YOUR CODE HERE
    cpuPercent = psutil.cpu_percent(interval=1)
    cpuCores = psutil.cpu_count(logical=True)

    win.addstr(3, 2, f"Total CPU Cores (Logical): {cpuCores}", curses.A_BOLD)
    win.addstr(4, 2, "Overall Usage:")
    drawBar(win, 4, 18, cpuPercent)

    # Per-core usage (display max 8 cores for simple layout)
    perCpu = psutil.cpu_percent(interval=1, percpu=True)
    win.addstr(6, 2, "Per-Core Usage:", curses.A_UNDERLINE)
    for i, p in enumerate(perCpu[:8]):
        win.addstr(7 + i, 2, f"Core {i}:")
        drawBar(win, 7 + i, 12, p, length=20)


    startY = 7 + min(len(perCpu), 8) + 2  # Calculate start position below core usage

    win.addstr(startY, 2, "Top 5 CPU Processes:", curses.A_BOLD | curses.A_UNDERLINE)

    # 1. Get all processes and sort them by CPU usage
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        processes.append(proc.info)

    # 2. Filter out processes that haven't registered CPU time yet (0.0)
    # 3. Sort by 'cpu_percent' in descending order
    # 4. Take the top 5
    topProcesses = sorted(
        [
            p
            for p in processes
            if p["cpu_percent"] is not None and p["cpu_percent"] > 0.0
        ],
        key=lambda p: p["cpu_percent"],
        reverse=True,
    )[:5]

    # 3. Display the top 5 processes
    win.addstr(startY + 1, 2, f"{'PID':<6} {'CPU %':<8} {'Name'}")

    for i, p in enumerate(topProcesses):
        y = startY + 2 + i
        if y < currentHeight - 1:  # Boundary check
            name = p["name"][: currentWidth - 25]  # Truncate name to fit screen
            win.addstr(y, 2, f"{p['pid']:<6} {p['cpu_percent']:<8.1f} {name}")


"""
   TODO This function will show multi threading capabilities.

   Two threads should be created.
    
   One used to call the function "printMsg1" provided above.

   A second thread should call the function "printMsg2" provided above.
"""


def showThreadingExample(win, currentHeight, currentWidth) -> None:
    # print("Demonstrating Threading")

    # TODO INSERT YOUR CODE HERE
    """multi-threading demo."""
    global threadLog

    # 1. Threading Demo
    win.addstr(3, 2, "Demonstrating Threading:", curses.A_BOLD)

    # Only run threads once
    if not threadLog:
        thread1 = threading.Thread(target=printMsg1, args=(5,))
        thread2 = threading.Thread(target=printMsg2, args=(10,))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    for i, msg in enumerate(threadLog):
        win.addstr(4 + i, 2, msg)

    # print("Done With Threading!")


"""
   TODO This function shows system error handling.

   Since out of memory, or out of disk space errors are difficult to create,
   we will use a divide by zero error and show the error handling being executed.
"""


def showErrorHandling(win, currentHeight, currentWidth) -> None:
    # print("Demonstrating Error Handling")
    # try:

    #    #TODO Insert your code here to cause a divide by zero error

    # except ZeroDivisionError:
    #     print("You can't divide by zero!")

    # except MemoryError:
    #     print("Memory Error!")

    # else:
    #     print("Result is", res)

    # finally:
    #     print("Execution complete.")

    # printBlankLines(2)
    # 2. Error Handling Demo
    win.addstr(8, 2, "Error Handling Demo:", curses.A_BOLD)
    try:
        # Causing a divide by zero error
        result = 100 / 0
        win.addstr(10, 2, f"Result is {result}")

    except ZeroDivisionError:
        win.addstr(
            10, 2, "ZeroDivisionError caught:", curses.color_pair(1) | curses.A_BOLD
        )
        win.addstr(11, 2, "You can't divide by zero!")

    except Exception as e:
        win.addstr(10, 2, f"Other Error: {e}")

    finally:
        win.addstr(13, 2, "Execution complete.")


PAGES = [
    getCpuStatistics,
    getMemoryStatistics,
    getFileDiskUsageStatistics,
    showThreadingExample,
    showErrorHandling,
]


def cursesApp(stdscr):

    global currentPage

    # Curses setup
    curses.curs_set(0)
    stdscr.nodelay(True)

    # Color error handling
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)  # for errors

    # resize variables
    lastSizeHeight, lastSizeWidth = stdscr.getmaxyx()
    lastTime = time.time()

    while True:
        # Get current dimensions
        currentHeight, currentWidth = stdscr.getmaxyx()

        # handle resizing
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
            f"Click through 1-5 for different options| Press 'q' to QUIT | Screen: {currentWidth}X{currentHeight}",
        )

        stdscr.refresh()

        # Handle Input
        key = stdscr.getch()
        if key != -1:  # Check if a key was pressed
            if key == quitKey:
                break

            # --- NEW NUMERIC NAVIGATION LOGIC ---
            # Check for keys '1' through '5'
            if ord("1") <= key <= ord("5"):
                # Convert the ASCII character code (e.g., ord('3')) to the integer value (3)
                # Subtract 1 to get the 0-based index (e.g., 3 - 1 = index 2)
                new_page_index = key - ord("1")

                # Check if the calculated index is within the defined pageCount
                if 0 <= new_page_index < pageCount:
                    currentPage = new_page_index

        time.sleep(0.1)


"""
   Main function, does not require modification.

   This calls the specific functions.
"""

def display_startup_banner():
    """Prints a non-curses banner before starting the TUI application."""
    print("=" * 60)
    print("━┏┛┏━┛┏━┛┃ ┃┏━┛┏━┛┏━┛┃ ┃┏━┃┏━┛  ┏━┛┏━┃┃  ┃ ┃━┏┛┛┏━┃┏━ ┏━┛")
    print(" ┃ ┏━┛┃  ┏━┃━━┃┏━┛┃  ┃ ┃┏┏┛┏━┛  ━━┃┃ ┃┃  ┃ ┃ ┃ ┃┃ ┃┃ ┃━━┃")
    print(" ┛ ━━┛━━┛┛ ┛━━┛━━┛━━┛━━┛┛ ┛━━┛  ━━┛━━┛━━┛━━┛ ┛ ┛━━┛┛ ┛━━┛")
    print(" System Optimization Benchmarker")
    print("=" * 60)
    print("\nStarting application... Press Enter to continue.")

    # Wait for the user to acknowledge the banner
    input()


if __name__ == "__main__":

    display_startup_banner()

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
