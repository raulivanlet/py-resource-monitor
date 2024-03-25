import threading
import platform
import psutil
import curses
import time
import os

# import sys
run_program=True
last_key=0
sort_by_type=1
selected_index=1
selected_index_max=40

def StillRun(window):
    global run_program, last_key, sort_by_type, selected_index, selected_index_max
    k=0
    maximum_keys = 8
    while (last_key != ord('q')):
        last_key = window.getch() 
        if (last_key == curses.KEY_LEFT):
            if (sort_by_type == 1):
                sort_by_type = maximum_keys
            else:
                sort_by_type = sort_by_type - 1
        elif (last_key == curses.KEY_RIGHT):
            if (sort_by_type == maximum_keys):
                sort_by_type = 1
            else:
                sort_by_type = sort_by_type + 1


        if (last_key == curses.KEY_DOWN):
            if (selected_index == selected_index_max):
                selected_index = 1
            else:
                selected_index = selected_index + 1
        elif (last_key == curses.KEY_UP):
            if (selected_index == 1):
                selected_index = selected_index_max
            else:
                selected_index = selected_index - 1

    run_program=False


def draw_menu(ncurses):
    global run_program, last_key, sort_by_type, selected_index, selected_index_max
    curses.curs_set(0)      # Hide the cursor
    ncurses.clear()         # Clear the canvas
    ncurses.refresh()       # Redraw the screen

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # Initialization
    height, width = ncurses.getmaxyx()
    center_point = height // 2 - height // 15

    if height <= 18 | width <= 68 :

        if height <= 18:
            message = "console height <= 18 characters"
            ncurses.addstr(center_point -1, (width - len(message)) // 2, message)

            message = "Please increse console height before proceeding."
            ncurses.addstr(center_point +1, (width - len(message)) // 2, message)

        if width <= 68:
            message = "Consl width"
            ncurses.addstr(center_point -1, (width - len(message)) // 2, message)

            message = "<= 68 chr"
            ncurses.addstr(center_point , (width - len(message)) // 2, message)
            
            message = "Inc consl wdt"
            ncurses.addstr(center_point +1, (width - len(message)) // 2, message)

        # Wait for user input
        ncurses.getch()
    
    else:

        # Print a welcome message
        message = "Welcome to the Raul's System Monitor program"
        ncurses.addstr(center_point -2, (width - len(message)) // 2, message)

        # Press Enter
        message = "Press key 'Enter' key to proceed."
        ncurses.addstr(center_point +2, (width - len(message)) // 2, message)

        # Wait for user input
        while True:
            key = ncurses.getch()

            # Continue if user presses Enter
            if key == ord('\n'):
                break
        ncurses.clear()

        # Thread
        thread_input = threading.Thread(target=StillRun, args=(ncurses,))
        thread_input.start()

        while run_program:

            # Get All Processes
            processes = []
            for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    process_info = process.info
                    memory_info = process_info['memory_info'].rss
                    memory_info = (float(memory_info)/1048576)
                    processes.append((process_info['pid'], process_info['name'], process_info['cpu_percent'], memory_info))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if sort_by_type == 1:
                processes.sort(key=lambda x: x[0], reverse=True)        # 1 = PID descending
            if sort_by_type == 2:
                processes.sort(key=lambda x: x[0], reverse=False)       # 2 = PID ascending
            
            if sort_by_type == 3:
                processes.sort(key=lambda x: x[1], reverse=True)        # 3 = Name descending
            if sort_by_type == 4:
                processes.sort(key=lambda x: x[1], reverse=False)       # 4 = Name ascending
            
            if sort_by_type == 5:
                processes.sort(key=lambda x: x[2], reverse=True)        # 5 = CPU Perc descending
            if sort_by_type == 6:
                processes.sort(key=lambda x: x[2], reverse=False)       # 6 = CPU Perc ascending

            if sort_by_type == 7:
                processes.sort(key=lambda x: x[3], reverse=True)        # 7 = MEM Perc descending
            if sort_by_type == 8:
                processes.sort(key=lambda x: x[3], reverse=False)       # 8 = MEM Perc ascending
            
            #Pannel Height
            panel1_height = 7
            panel2_height = 7 
            panel3_height = 6
            panel4_height = height - panel1_height - panel3_height + 1
            panel4_items = panel4_height - 2

            #Pannel width
            panel1_width = width // 2
            panel2_width = width - panel1_width
            panel3_width = width
            panel4_width = width

            panel4_id_width = 8
            panel4_name_width = 40
            panel4_cpu_width = 8
            panel4_mem_width = 8

            panel4_id_pos = 2
            panel4_name_pos = 1 + panel4_id_pos + panel4_id_width + 1
            panel4_cpu_pos = panel4_name_pos + panel4_name_width + 1
            panel4_mem_pos = panel4_cpu_pos + panel4_cpu_width + 1            

            # Declaration of strings
            header = "Scrollable Panel - Press 'q' to quit"
            keystr = "Pressed: {}".format(last_key)[:width-1]
            statusbarstr = f"Press 'q' to quit | Last key keycode: {keystr} | Wh: {width}, Ht: {height} "

            # Print values
            user_name=(os.getlogin()if os.name == 'posix' else os.environ['USERNAME'])
            platform_version=platform.version()[4:18]
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_total = "%0.2f" % (psutil.virtual_memory().total / (1024.**3))
            memory_total_used = "%0.2f" % (psutil.virtual_memory().used / (1024.**3))
            memory_total_swap = "%0.2f" % (psutil.swap_memory().total / (1024.**3))
            disk_total = "%0.2f" % (psutil.disk_usage("/").total / (1024.**3))
            disk_total_used = "%0.2f" % (psutil.disk_usage("/").used / (1024.**3))
            

            selected_index_max = panel4_items - 1

            # Create windows for the two panels
            panel1 = curses.newwin(panel1_height, panel1_width, 0, 0)
            panel2 = curses.newwin(panel2_height, panel2_width +1, 0, panel1_width -1)
            panel3 = curses.newwin(panel3_height, panel3_width, panel1_height -1, 0)
            panel4 = curses.newwin(panel4_height, panel4_width, panel1_height + panel3_height -2, 0)

            # Draw borders around the panels
            panel1.border('|', '|', '-', '-', '+', '+', '+', '+')
            panel2.border('|', '|', '-', '-', '+', '+', '+', '+')
            panel3.border('|', '|', '-', '-', '+', '+', '+', '+')
            panel4.border('|', '|', '-', '-', '+', '+', '+', '+')

            # Add content to the panel 1
            panel1.addstr(1, 2 , "System: " + platform.system())
            panel1.addstr(2, 2 , "Release: " + platform.release())
            panel1.addstr(3, 2 , "Username: " + user_name)
            panel1.addstr(4, 2 , "Device Name: " + platform.node())
            panel1.addstr(5, 2 , "Version: " + platform_version)

            # Add content to the panel 2
            panel2.addstr(1, 2 , "Processor: " + platform.processor())
            panel2.addstr(2, 2 , "CPU Vendor: " )
            panel2.addstr(3, 2 , "CPU Cores: " + str(psutil.cpu_count()))
            panel2.addstr(4, 2 , "RAM: " + str(memory_total) + " Gb")
            panel2.addstr(5, 2 , "Swap Size: " + str(memory_total_swap) + " Gb")

            # Add content to the panel 3
            panel3.addstr(1, 2 , "CPU Usage: " + str(cpu_usage) + " %")
            panel3.addstr(2, 2 , "RAM Usage: " + str(memory_total_used) + " / " + str(memory_total) + " Gb")
            panel3.addstr(3, 2 , "Disk Used: " + str(psutil.disk_usage("/").percent) + "%")
            panel3.addstr(4, 2 , "Disk Used: " + str(disk_total_used) + " / " + str(disk_total) + " Gb" )

            # Add content to the panel 4
            if sort_by_type == 1:
                panel4.addstr(1, panel4_id_pos , "PID \/:", curses.color_pair(2))
            elif sort_by_type == 2:
                panel4.addstr(1, panel4_id_pos , "PID /\:", curses.color_pair(2))
            else:
                panel4.addstr(1, panel4_id_pos , "PID:", curses.color_pair(1))
            
            if sort_by_type == 3:
                panel4.addstr(1, panel4_name_pos , "Name \/:", curses.color_pair(2))
            elif sort_by_type == 4:
                panel4.addstr(1, panel4_name_pos , "Name /\:", curses.color_pair(2))
            else:
                panel4.addstr(1, panel4_name_pos , "Name:", curses.color_pair(1))
            
            if sort_by_type == 5:
                panel4.addstr(1, panel4_cpu_pos , "CPU \/:", curses.color_pair(2))
            elif sort_by_type == 6:
                panel4.addstr(1, panel4_cpu_pos , "CPU /\:", curses.color_pair(2))
            else:
                panel4.addstr(1, panel4_cpu_pos , "CPU:", curses.color_pair(1))

            if sort_by_type == 7:
                panel4.addstr(1, panel4_mem_pos , "MEM \/:", curses.color_pair(2))
            elif sort_by_type == 8:
                panel4.addstr(1, panel4_mem_pos , "MEM /\:", curses.color_pair(2))
            else:
                panel4.addstr(1, panel4_mem_pos , "MEM:", curses.color_pair(1))

            panel4_index=1
            for pid, name, cpu_usage, memory_info in processes:
                if panel4_index < panel4_items:
                    if (panel4_index == selected_index):
                        panel4_index = panel4_index + 1
                        panel4.attron(curses.color_pair(3))
                        panel4.addstr(panel4_index, panel4_id_pos , (f"{pid}"))
                        panel4.addstr(panel4_index, panel4_name_pos , (f"{name[:panel4_name_width]}"))
                        panel4.addstr(panel4_index, panel4_cpu_pos , (f"{cpu_usage:.2f}%"))
                        panel4.addstr(panel4_index, panel4_mem_pos , (f"{memory_info:.0f}Mb"))
                        panel4.attroff(curses.color_pair(3))
                    else:
                        panel4_index = panel4_index + 1
                        panel4.addstr(panel4_index, panel4_id_pos , (f"{pid}"))
                        panel4.addstr(panel4_index, panel4_name_pos , (f"{name[:panel4_name_width]}"))
                        panel4.addstr(panel4_index, panel4_cpu_pos , (f"{cpu_usage:.2f}%"))
                        panel4.addstr(panel4_index, panel4_mem_pos , (f"{memory_info:.0f}Mb"))

            # Display a header
            ncurses.addstr(0, (width - len(header)) // 2, header, curses.A_BOLD)            

            # Turning on attributes for title
            ncurses.attron(curses.color_pair(3))
            ncurses.attron(curses.A_BOLD)
            ncurses.addstr(height-1, 0 , " " * (width - 1))
            ncurses.addstr(height-1, 0, statusbarstr)
            ncurses.attroff(curses.color_pair(3))
            ncurses.attroff(curses.A_BOLD)

            # Refresh the screen to display the panels
            panel1.refresh()
            panel2.refresh()
            panel3.refresh()
            panel4.refresh()
            ncurses.refresh()

            # Wait x seconds until next refresh
            time.sleep(0.1)

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()

