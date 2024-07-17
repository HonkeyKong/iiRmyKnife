import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os, subprocess, zipfile, re
from tkinterdnd2 import DND_FILES, TkinterDnD
from lxml import etree
import platform

if platform.system() == "Windows":
    import win32gui, win32con, ctypes


VERSION_NUMBER = "0.10"
debugEnabled = False

def writeLog(*logText):
    if(debugEnabled):
        for line in logText:
            print("[iiRmyKnife]:", ' '.join(map(str, logText)))

def minimize_console():
    if platform.system() == "Windows":
        # Get the console window handle
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        
        if hwnd:
            # Minimize the window
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

# Minimize the console window at the start
minimize_console()

# Initialize the main window
# Load the tkdnd library
root = TkinterDnD.Tk()
root.title(f"iiRmyKnife v{VERSION_NUMBER} by HonkeyKong")

# Set the grid layout
root.grid_columnconfigure((0, 1, 2), weight=1)
root.grid_rowconfigure((0, 1, 2), weight=1)

# Global variable to store the selected device's serial number
selected_device_serial = ""

# Define button actions
def push_cfg():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    selected_device = selected_device_serial

    ## Use this function to load from an external XSD file.

    # # Load XSD
    # with open("mameconfig.xsd", 'r') as xsd_file:
    #     schema_root = etree.XML(xsd_file.read())
    # schema = etree.XMLSchema(schema_root)

    # def validate_cfg(file_path):
    #     try:
    #         parser = etree.XMLParser(schema=schema)
    #         with open(file_path, 'r', encoding='utf-8') as f:
    #             file_content = f.read()
    #             # Ensure XML declaration is at the start
    #             if file_content.startswith('\ufeff'):
    #                 file_content = file_content.encode('utf-8')[3:].decode('utf-8')
    #             etree.fromstring(file_content, parser)
    #         return True
    #     except Exception as ex:
    #         messagebox.showerror("Error", f"Validation failed: {ex}")
    #         writeLog(f"Validation failed: {ex}")
    #         return False


    def validate_cfg(file_path):
        xsd_data = """
           <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="mameconfig">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="system" type="SystemType" maxOccurs="unbounded"/>
                    </xs:sequence>
                    <xs:attribute name="version" type="xs:string" use="required"/>
                </xs:complexType>
            </xs:element>

            <xs:complexType name="SystemType">
                <xs:choice maxOccurs="unbounded">
                    <xs:element name="input" type="InputType" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element name="video" type="VideoType" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element name="counters" type="CountersType" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element name="ui_warnings" type="UIWarningsType" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element name="crosshairs" type="CrosshairsType" minOccurs="0" maxOccurs="unbounded"/>
                    <xs:element name="mixer" type="MixerType" minOccurs="0" maxOccurs="unbounded"/>
                </xs:choice>
                <xs:attribute name="name" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="InputType">
                <xs:sequence>
                    <xs:element name="port" type="PortType" maxOccurs="unbounded"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="PortType" mixed="true">
                <xs:sequence>
                    <xs:element name="newseq" type="NewSeqType" minOccurs="0" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:attribute name="tag" type="xs:string" use="required"/>
                <xs:attribute name="type" type="xs:string" use="required"/>
                <xs:attribute name="mask" type="xs:string" use="required"/>
                <xs:attribute name="defvalue" type="xs:string" use="required"/>
                <xs:attribute name="keydelta" type="xs:string" use="optional"/>
                <xs:attribute name="centerdelta" type="xs:string" use="optional"/>
                <xs:attribute name="reverse" type="xs:string" use="optional"/>
                <xs:attribute name="value" type="xs:string" use="optional"/>
                <xs:attribute name="sensitivity" type="xs:string" use="optional"/>
            </xs:complexType>

            <xs:complexType name="NewSeqType">
                <xs:simpleContent>
                    <xs:extension base="xs:string">
                        <xs:attribute name="type" type="xs:string" use="required"/>
                        <xs:attribute name="sensitivity" type="xs:string" use="optional"/>
                    </xs:extension>
                </xs:simpleContent>
            </xs:complexType>

            <xs:complexType name="VideoType">
                <xs:sequence>
                    <xs:element name="target" type="TargetType" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:anyAttribute processContents="lax"/>
            </xs:complexType>

            <xs:complexType name="TargetType">
                <xs:attribute name="index" type="xs:string" use="required"/>
                <xs:attribute name="view" type="xs:string" use="optional"/>
                <xs:attribute name="rotate" type="xs:string" use="optional"/>
            </xs:complexType>

            <xs:complexType name="CountersType">
                <xs:sequence>
                    <xs:element name="coins" type="CoinsType" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:anyAttribute processContents="lax"/>
            </xs:complexType>

            <xs:complexType name="CoinsType">
                <xs:attribute name="index" type="xs:string" use="required"/>
                <xs:attribute name="number" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="UIWarningsType">
                <xs:sequence>
                    <xs:element name="feature" type="FeatureType" minOccurs="0" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:attribute name="launched" type="xs:string" use="optional"/>
                <xs:attribute name="warned" type="xs:string" use="optional"/>
            </xs:complexType>

            <xs:complexType name="FeatureType">
                <xs:attribute name="device" type="xs:string" use="required"/>
                <xs:attribute name="type" type="xs:string" use="required"/>
                <xs:attribute name="status" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="CrosshairsType">
                <xs:sequence>
                    <xs:element name="crosshair" type="CrosshairType" maxOccurs="unbounded"/>
                    <xs:element name="autotime" type="AutoTimeType" minOccurs="0"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="CrosshairType">
                <xs:attribute name="player" type="xs:string" use="required"/>
                <xs:attribute name="mode" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="AutoTimeType">
                <xs:attribute name="val" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="MixerType">
                <xs:sequence>
                    <xs:element name="channel" type="ChannelType" maxOccurs="unbounded"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="ChannelType">
                <xs:attribute name="index" type="xs:string" use="required"/>
                <xs:attribute name="newvol" type="xs:string" use="required"/>
            </xs:complexType>
        </xs:schema>
        """

        try:
            from lxml import etree
            schema_root = etree.XML(xsd_data)
            schema = etree.XMLSchema(schema_root)
            parser = etree.XMLParser(schema=schema, recover=True)  # Enable recovery mode

            # Read/print the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                # writeLog("File Content:\n", file_content)  # Debugging line
                doc = etree.fromstring(file_content, parser)

                # Validate the parsed document against the schema
                schema.assertValid(doc)

            return True
        except etree.DocumentInvalid as ex:
            messagebox.showerror("Error", f"Validation failed: {ex}")
            writeLog(f"Validation failed: {ex}")
            return False
        except Exception as ex:
            messagebox.showerror("Error", f"Error occurred: {ex}")
            writeLog(f"Error occurred: {ex}")
            return False

    def select_cfg():
        global push_files, multi_files
        file_path = filedialog.askopenfilename(
            title="Select a CFG file",
            filetypes=[("CFG files", "*.cfg")]
        )
        push_cfg_window.lift()  # Re-lift after file dialog is opened
        push_cfg_window.focus_force()  # Ensure window regains focus
        if file_path and os.path.exists(file_path):
            if validate_cfg(file_path):
                lbl_cfg_file.config(text="File opened: " + file_path)
                push_files = [file_path]
                multi_files = False
            else:
                push_files = []
                lbl_cfg_file.config(text="No valid file selected.")

    def push_cfg_file():
        global selected_device, push_files, multi_files
        if not selected_device_serial:
            messagebox.showerror("Error", "Select a device first.")
            return
        
        selected_device = selected_device_serial

        if not push_files:
            messagebox.showerror("Error", "Select a CFG file first.")
            return

        # Check if the files exist
        for file_path in push_files:
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"CFG file {file_path} does not exist.")
                return

        # Run adb root command
        adb_root_cmd = ["adb", "-s", selected_device, "root"]
        writeLog("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the CFG files
        pushError = False
        for file_path in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", file_path, "/sdcard/Android/data/org.emulator.arcade/files/cfg/"]
            writeLog("Running ADB Command:", push_cmd)
            if run_adb_command(push_cmd) == None:
                pushError = True

        if(pushError):
            messagebox.showerror("Error", "CFG push failed.")
        else:
            messagebox.showinfo("Success", "CFG file(s) pushed.")
        
        if not light_gun_var.get():
            return

        if multi_files:
            messagebox.showerror("Error", "Sorry, only one light gun game can be configured at a time.")
            return

        cfg_names = push_files[0].split('\\')  # Use the first file in the list
        rom_name = cfg_names[-1].split('.')[0]
        lg_push_cmd = ["adb", "-s", selected_device, "push", "lightgun.zip", f"/sdcard/Android/data/org.emulator.arcade/files/artwork/lightgun/{rom_name.split('/')[-1]}.zip"]
        writeLog("Running ADB Command:", lg_push_cmd)
        if run_adb_command(lg_push_cmd) == None:
            pushError = True
        if(pushError):
            messagebox.showerror("Error", "Error setting up light gun.")
            return
        
        db_loc = "/data/data/com.iircade.iiconsole/databases/Game.db"
        db_update_cmd = f"\"update GAME set Reserve1='T#0#1' where GAME.ID='{rom_name.split('/')[-1]}.zip';\""
        print("DB Update command = ", db_update_cmd)
        db_exec_cmd = ["adb", "-s", selected_device, "shell", "sqlite3", db_loc, db_update_cmd]
        writeLog("Running ADB Command:", db_exec_cmd)
        if run_adb_command(db_exec_cmd) == None:
            pushError = True
        if(pushError):
            messagebox.showerror("Error", "Light Gun setup failed.")
            return
        else:
            messagebox.showinfo("Success", "Light Gun setup successful.")

    # Use TkinterDnD.Toplevel for the new window
    push_cfg_window = tk.Toplevel(root)
    push_cfg_window.title("Push CFG")
    push_cfg_window.lift()  # Ensure the window is above the main window
    push_cfg_window.focus_force()  # Ensure the window gets focus

    # Bind focus events to keep the window on top
    push_cfg_window.bind("<FocusIn>", lambda e: push_cfg_window.lift())
    push_cfg_window.bind("<Configure>", lambda e: push_cfg_window.lift())

    tk.Button(push_cfg_window, text="Select CFG", command=select_cfg).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(push_cfg_window, text="Push CFG", command=push_cfg_file).grid(row=1, column=0, padx=10, pady=10)

    light_gun_var = tk.BooleanVar()
    tk.Checkbutton(push_cfg_window, text="Light Gun", variable=light_gun_var).grid(row=2, column=0, padx=10, pady=10)

    lbl_cfg_file = tk.Label(push_cfg_window, text="Select a CFG file with the button above, or drag & drop here.")
    lbl_cfg_file.grid(row=3, column=0, columnspan=1, padx=10, pady=10)

    def on_drag_enter(event):
        event.widget.focus_force()
        event.widget.config(relief="sunken")

    def on_drag_leave(event):
        event.widget.config(relief="raised")

    def on_drop(event):
        # Use regular expression to extract file paths
        files = re.findall(r'\{.*?\}|\S+', event.data)
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            # Remove curly braces if present
            cleaned_file = files[0].strip('{}')
            writeLog(f"Validating {cleaned_file}...")
            if validate_cfg(cleaned_file):
                multi_files = False
                push_files = [cleaned_file]
                lbl_cfg_file.config(text=f"File opened: {cleaned_file}")
        else:
            multi_files = True
            valid_files = []
            for file in files:
                # Remove curly braces if present
                cleaned_file = file.strip('{}')
                writeLog(f"Validating {cleaned_file}...")
                if os.path.exists(cleaned_file):
                    if validate_cfg(cleaned_file):
                        valid_files.append(cleaned_file)
                    else:
                        writeLog(f"File {cleaned_file} not valid.")
                else:
                    writeLog(f"File {cleaned_file} does not exist.")
            if valid_files:
                push_files = valid_files
                lbl_cfg_file.config(text=f"{len(valid_files)} files loaded.")
            else:
                push_files = []
                lbl_cfg_file.config(text="No valid file selected.")
                messagebox.showerror("Error", "No valid CFG files were selected.")
                
    push_cfg_window.drop_target_register(DND_FILES)
    push_cfg_window.dnd_bind('<<DragEnter>>', on_drag_enter)
    push_cfg_window.dnd_bind('<<DragLeave>>', on_drag_leave)
    push_cfg_window.dnd_bind('<<Drop>>', on_drop)

def fix_clock():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    def apply_timezone():
        serial_number = selected_device_serial
        timezone_selection = timezone_var.get()

        timezone_dict = {
            "Eastern Time (ET)": "GMT-05:00",
            "Central Time (CT)": "GMT-06:00",
            "Mountain Time (MT)": "GMT-07:00",
            "Pacific Time (PT)": "GMT-08:00"
        }

        if timezone_selection in timezone_dict:
            timezone = timezone_dict[timezone_selection]
        else:
            timezone = custom_timezone_entry.get()

        command = ["adb", "-s", serial_number, "shell", "setprop", "persist.sys.timezone", timezone]
        run_adb_command(command)

        dst_offset_dict = {
            "Eastern Time (ET)": "GMT-04:00",
            "Central Time (CT)": "GMT-05:00",
            "Mountain Time (MT)": "GMT-06:00",
            "Pacific Time (PT)": "GMT-07:00"
        }

        if timezone_selection in dst_offset_dict:
            dst_offset = dst_offset_dict[timezone_selection]
            command = ["adb", "-s", serial_number, "shell", "setprop", "persist.sys.timezone", dst_offset]
            run_adb_command(command)

        command = ["adb", "-s", serial_number, "shell", "settings", "put", "global", "ntp_server", "time.nist.gov"]
        run_adb_command(command)
        command = ["adb", "-s", serial_number, "shell", "settings", "put", "global", "auto_time", "1"]
        run_adb_command(command)
        command = ["adb", "-s", serial_number, "shell", "am", "broadcast", "-a", "android.intent.action.TIME_SET"]
        run_adb_command(command)
        command = ["adb", "-s", serial_number, "shell", "am", "broadcast", "-a", "android.intent.action.TIMEZONE_CHANGED"]
        run_adb_command(command)

        messagebox.showinfo("Success", "Clock should be fixed now.")
        clock_fix_window.destroy()

    def on_timezone_change(event):
        if timezone_var.get() == "Other":
            custom_timezone_label.grid(row=1, column=0, padx=10, pady=10)
            custom_timezone_entry.grid(row=1, column=1, padx=10, pady=10)
        else:
            custom_timezone_label.grid_forget()
            custom_timezone_entry.grid_forget()

    clock_fix_window = tk.Toplevel(root)
    clock_fix_window.title("Fix Clock")

    tk.Label(clock_fix_window, text="Select Time Zone:").grid(row=0, column=0, padx=10, pady=10)

    timezone_var = tk.StringVar(value="Eastern Time (ET)")
    timezone_combobox = ttk.Combobox(clock_fix_window, textvariable=timezone_var)
    timezone_combobox['values'] = [
        "Eastern Time (ET)",
        "Central Time (CT)",
        "Mountain Time (MT)",
        "Pacific Time (PT)",
        "Other"
    ]
    timezone_combobox.grid(row=0, column=1, padx=10, pady=10)
    timezone_combobox.bind("<<ComboboxSelected>>", on_timezone_change)

    custom_timezone_label = tk.Label(clock_fix_window, text="Enter GMT offset (e.g., GMT+03:00):")
    custom_timezone_entry = tk.Entry(clock_fix_window)

    tk.Button(clock_fix_window, text="Apply", command=apply_timezone).grid(row=2, column=0, columnspan=2, pady=10)

# Path to the SQLite database
DATABASE_PATH = "/data/data/com.iircade.iiconsole/databases/Game.db"

# Path to the game folder on the device
GAME_FOLDER_PATH = "/sdcard/Game/Games"

def game_manager():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return
    selected_device = selected_device_serial

    def uninstall_game(game_id):
        pushError = False
        errorString = ""
        
        # Retrieve image paths before deleting the game
        jpeg_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, f"\"SELECT ImgBg,ImgINST FROM GAME WHERE ID='{game_id}';\""]
        jpegs = run_adb_command(jpeg_command)
        if jpegs is None:
            errorString += "Failed to retrieve BKG/INS images.\n"
            pushError = True
        else:
            jpegs = jpegs.split('|')
            bkgImg = jpegs[0]
            insImg = jpegs[1]

        # Delete the game and config entries
        db_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, f"\"DELETE FROM GAME WHERE ID='{game_id}';\""]
        config_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, f"\"DELETE FROM CONFIG WHERE ID='{game_id}';\""]
        
        if run_adb_command(db_command) is None:
            errorString += "Failed to delete from GAME database.\n"
            pushError = True
        if run_adb_command(config_command) is None:
            errorString += "Failed to delete from CONFIG database.\n"
            pushError = True
        
        if pushError:
            messagebox.showerror("Error", errorString)
            return

        # Remove the game file
        if game_id.endswith(".zip"):  # MAME ROM
            remove_command = ["adb", "-s", selected_device, "shell", "rm", f"\"{GAME_FOLDER_PATH}/{game_id}\""]
            if run_adb_command(remove_command) is not None:
                messagebox.showinfo("Success", f"MAME ROM {game_id} uninstalled.")
            else:
                messagebox.showerror("Error", f"Error deleting {game_id}")
        else:  # Android application
            uninstall_command = ["adb", "-s", selected_device, "uninstall", game_id]
            if run_adb_command(uninstall_command) is not None:
                messagebox.showinfo("Success", f"Android app {game_id} uninstalled.")
            else:
                messagebox.showerror("Error", f"Error deleting {game_id}")

        # Delete the background image
        if bkgImg:
            writeLog(f"Deleting {bkgImg}...")
            bkgDelete = ["adb", "-s", selected_device, "shell", "rm", f"\"/sdcard/Game/Background/{bkgImg}\""]
            if run_adb_command(bkgDelete) is None:
                messagebox.showerror("Error", f"Error deleting {bkgImg}")

        # Delete the instruction image
        if insImg:
            writeLog(f"Deleting {insImg}...")
            insDelete = ["adb", "-s", selected_device, "shell", "rm", f"\"/sdcard/Game/Instruction/{insImg}\""]
            if run_adb_command(insDelete) is None:
                messagebox.showerror("Error", f"Error deleting {insImg}")

    def list_installed_games():
        # Query the SQLite database for all games
        selected_device = selected_device_serial
        query_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, "\"SELECT * FROM GAME;\""]
        output = run_adb_command(query_command)
        if output:
            games = output.split('\n')
            game_details = []
            for game in games:
                details = game.split('|')
                if len(details) >= 4:  # Ensure there are enough elements
                    game_number = details[0]
                    game_id = details[1]
                    game_name = details[3]
                    game_details.append((game_number, game_id, game_name))
                else:
                    writeLog(f"Unexpected game format: {game}")  # Log unexpected formats

            # Sort the game_details list alphabetically by game_id
            sorted_games = sorted(game_details, key=lambda x: x[2])

            game_listbox.delete(0, tk.END)  # Clear existing entries
            for game_number, game_id, game_name in sorted_games:
                game_listbox.insert(tk.END, f"Number: {game_number}, ID: {game_id}, Name: {game_name}")

    def uninstall_game_prompt():
        selected = game_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No game selected.")
            return

        selected_index = selected[0]
        game_info = game_listbox.get(selected_index)
        try:
            game_id = game_info.split(", ID: ")[1].split(", Name:")[0]
            game_name = game_info.split(", Name: ")[1]
        except IndexError:
            messagebox.showerror("Error", "Failed to parse game info.")
            return

        confirm = messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall the game '{game_name}'?")
        if confirm:
            uninstall_game(game_id)
            list_installed_games()

    def extract_game():
        selected = game_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No game selected.")
            return

        selected_index = selected[0]
        game_info = game_listbox.get(selected_index)
        try:
            game_id = game_info.split(", ID: ")[1].split(", Name:")[0]
            game_name = game_info.split(", Name: ")[1]
        except IndexError:
            messagebox.showerror("Error", "Failed to parse game info.")
            return

        if not game_id:
            return

        if game_id.split('.')[-1].lower() != "zip":
            messagebox.showerror("Error", "Game ID must be a MAME ROM.")
            return

        game_command = ["adb", "-s", selected_device_serial, "shell", "sqlite3", DATABASE_PATH, f"\"SELECT Version,Name,Genre,GameType,HDMIOut,Rating,JoystickType,Display,ImgBg,ImgINST FROM GAME WHERE ID='{game_id}';\""]
        writeLog(f"Running command: {' '.join(game_command)}")  # Debugging line
        game_data = run_adb_command(game_command)
        if game_data is None:
            messagebox.showerror("Error", "Could not extract game info.")
            return
        game_data = game_data.split('|')

        cfg_content = ""
        column = 0
        while column < 8:
            cfg_content += f"{game_data[column]}#\n"
            column += 1

        config_command = ["adb", "-s", selected_device_serial, "shell", "sqlite3", DATABASE_PATH, f"\"SELECT Keymap FROM CONFIG WHERE ID='{game_id}';\""]
        writeLog(f"Running command: {' '.join(config_command)}")  # Debugging line
        config_data = run_adb_command(config_command)
        if config_data is None:
            messagebox.showerror("Error", "Could not extract config info.")
            return
        config_data = config_data.split('#')
        for map in config_data:
            line = map.strip('\n')
            cfg_content += f"{line}#\n"

        bgImg = game_data[8]
        insImg = game_data[9]
        writeLog(f"Background image: {bgImg}")
        writeLog(f"Instruction image: {insImg}")

        bg_img_path = f"/sdcard/Game/Background/{bgImg}"
        ins_img_path = f"/sdcard/Game/Instruction/{insImg}"

        # Pull the background image
        bg_cmd = ["adb", "-s", selected_device_serial, "pull", bg_img_path]
        writeLog(f"Running command: {' '.join(bg_cmd)}")  # Debugging line
        if run_adb_command(bg_cmd) is None:
            writeLog(f"Error retrieving background image: {bg_img_path}")
            messagebox.showerror("Error", f"Error retrieving background image: {bg_img_path}")

        # Pull the instruction image
        ins_cmd = ["adb", "-s", selected_device_serial, "pull", ins_img_path]
        writeLog(f"Running command: {' '.join(ins_cmd)}")  # Debugging line
        if run_adb_command(ins_cmd) is None:
            writeLog(f"Error retrieving instruction image: {ins_img_path}")
            messagebox.showerror("Error", f"Error retrieving instruction image: {ins_img_path}")

        game_path = f"/sdcard/Game/Games/{game_id}"
        game_cmd = ["adb", "-s", selected_device_serial, "pull", game_path]
        writeLog(f"Running command: {' '.join(game_cmd)}")  # Debugging line
        if run_adb_command(game_cmd) is None:
            writeLog(f"Error retrieving game ROM: {game_path}")
            messagebox.showerror("Error", f"Error retrieving game ROM: {game_path}")

        # Write the CFG file
        cfg_filename = f"{game_id.split('.')[0]}.cfg"
        with open(cfg_filename, 'w', encoding='utf-8') as cfg_file:
            cfg_file.write(cfg_content)

        # Create ZIP file structure
        zip_filename = f"{game_id.split('.')[0]}_extracted.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            zipf.write(cfg_filename, f"games/{cfg_filename}")

            if os.path.exists(bgImg):
                zipf.write(bgImg, f"games/background/{bgImg}")
            if os.path.exists(insImg):
                zipf.write(insImg, f"games/instruction/{insImg}")
            if os.path.exists(game_id):
                zipf.write(game_id, f"games/games/{game_id}")

        # Clean up temporary files
        os.remove(cfg_filename)
        if os.path.exists(bgImg):
            os.remove(bgImg)
        if os.path.exists(insImg):
            os.remove(insImg)
        if os.path.exists(game_id):
            os.remove(game_id)

        messagebox.showinfo("Success", f"Game {game_id} extracted and zipped successfully.")


    # Create the game manager window
    game_manager_window = tk.Toplevel(root)
    game_manager_window.title("iiRcade Game Manager")

    # Create a frame for the buttons
    button_frame = tk.Frame(game_manager_window)
    button_frame.pack(pady=10)

    # List games button
    list_button = tk.Button(button_frame, text="List Games", command=list_installed_games)
    list_button.pack(side=tk.LEFT, padx=5)

    # Uninstall game button
    uninstall_button = tk.Button(button_frame, text="Uninstall Game", command=uninstall_game_prompt)
    uninstall_button.pack(side=tk.LEFT, padx=5)

    # Extract game button
    extract_button = tk.Button(button_frame, text="Extract Game", command=extract_game)
    extract_button.pack(side=tk.LEFT, padx=5)

    # Create a listbox to display the list of games
    global game_listbox
    game_listbox = tk.Listbox(game_manager_window, width=80, height=20)
    game_listbox.pack(pady=10)


def push_artwork():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    selected_device = selected_device_serial

    def select_artwork():
        global push_files, multi_files
        file_path = filedialog.askopenfilename(
            title="Select a bezel file",
            filetypes=[("MAME Bezel files", "*.zip")]
        )
        push_artwork_window.lift()  # Re-lift after file dialog is opened
        push_artwork_window.focus_force()  # Ensure window regains focus

        # Verify that a ZIP file is selected and exists
        if file_path and file_path.lower().endswith('.zip') and os.path.exists(file_path):
            lbl_artwork_file.config(text="File opened: " + file_path)
            push_files = [file_path]  # Store as list
            multi_files = False
        else:
            push_files = []
            lbl_artwork_file.config(text="No valid file selected.")
            if file_path and not file_path.lower().endswith('.zip'):
                messagebox.showerror("Error", "Selected file is not a ZIP file.")

    def push_artwork_file():
        global selected_device, push_files, multi_files
        if not selected_device_serial:
            messagebox.showerror("Error", "Select a device first.")
            return
        
        selected_device = selected_device_serial

        if not push_files:
            messagebox.showerror("Error", "Select a bezel file first.")
            return

        # Create the directory in case it doesn't exist.
        run_adb_command(["adb", "-s", selected_device_serial, "shell", "mkdir", "-p", "/sdcard/Android/data/org.emulator.arcade/files/artwork"])

        # Check if the files exist
        writeLog(f"push_files contents: {push_files}")
        for file_path in push_files:
            writeLog("Checking file ", file_path)
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"Bezel file {file_path} does not exist.")
                return

        # Run adb root command
        adb_root_cmd = ["adb", "-s", selected_device, "root"]
        writeLog("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the artwork files
        for file_path in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", file_path.strip('{').strip('}'), "/sdcard/Android/data/org.emulator.arcade/files/artwork/"]
            writeLog("Running ADB Command:", push_cmd)
            if run_adb_command(push_cmd) is None:
                messagebox.showerror("Error", f"Failed to push {file_path}.")
                return
        
        messagebox.showinfo("Success", "All bezels pushed successfully.")

    # Use TkinterDnD.Toplevel for the new window
    push_artwork_window = tk.Toplevel(root)
    push_artwork_window.title("Push artwork")
    push_artwork_window.lift()  # Ensure the window is above the main window
    push_artwork_window.focus_force()  # Ensure the window gets focus

    # Bind focus events to keep the window on top
    push_artwork_window.bind("<FocusIn>", lambda e: push_artwork_window.lift())
    push_artwork_window.bind("<Configure>", lambda e: push_artwork_window.lift())

    tk.Button(push_artwork_window, text="Select Bezel", command=select_artwork).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(push_artwork_window, text="Push Bezels", command=push_artwork_file).grid(row=1, column=0, padx=10, pady=10)

    lbl_artwork_file = tk.Label(push_artwork_window, text="Select a bezel file with the button above, or drag & drop here.")
    lbl_artwork_file.grid(row=2, column=0, columnspan=1, padx=10, pady=10)

    def on_drag_enter(event):
        event.widget.focus_force()
        event.widget.config(relief="sunken")

    def on_drag_leave(event):
        event.widget.config(relief="raised")

    def on_drop(event):
        # Use regular expression to extract file paths
        files = re.findall(r'\{.*?\}|\S+', event.data)
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            multi_files = False
            # Remove curly braces if present
            cleaned_file = files[0].strip('{}')
            if os.path.exists(cleaned_file):
                push_files = [cleaned_file]  # Store as list
                lbl_artwork_file.config(text=f"File opened: {cleaned_file}")
            else:
                lbl_artwork_file.config(text="No valid file selected.")
                messagebox.showerror("Error", "Selected file does not exist.")
        else:
            multi_files = True
            valid_files = []
            for file in files:
                # Remove curly braces if present
                cleaned_file = file.strip('{}')
                if os.path.exists(cleaned_file):
                    valid_files.append(cleaned_file)
                else:
                    writeLog(f"File {cleaned_file} does not exist.")
                    messagebox.showerror("Error", f"File {cleaned_file} does not exist.")
            if valid_files:
                push_files = valid_files
                lbl_artwork_file.config(text=f"{len(valid_files)} files loaded.")
            else:
                push_files = []
                lbl_artwork_file.config(text="No valid file selected.")
                messagebox.showerror("Error", "No valid bezel files were selected.")

        writeLog("Final list of files to push:", push_files)



    push_artwork_window.drop_target_register(DND_FILES)
    push_artwork_window.dnd_bind('<<DragEnter>>', on_drag_enter)
    push_artwork_window.dnd_bind('<<DragLeave>>', on_drag_leave)
    push_artwork_window.dnd_bind('<<Drop>>', on_drop)


def reboot_cabinet():
    if not selected_device_serial:
        messagebox.showwarning("Warning", "No device selected")
        return

    serial_number = selected_device_serial
    command = ["adb", "-s", serial_number, "reboot"]
    run_adb_command(command)

def fix_license():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    selected_device = selected_device_serial

    db_loc = "/data/data/com.iircade.iiconsole/databases/Game.db"
    license_update_cmd = "\"update CONFIG set Preload='1';\""
    db_exec_cmd = ["adb", "-s", selected_device, "shell", "sqlite3", db_loc, license_update_cmd]

    writeLog("Running ADB Command:", db_exec_cmd)  # writeLog for debugging
    if run_adb_command(db_exec_cmd) == None:
        messagebox.showerror("Error", "License fix failed.")
    else:
        messagebox.showinfo("Success", "Licenses fixed.")


def push_sounds():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    selected_device = selected_device_serial

    def select_sample():
        global push_files, multi_files
        file_path = filedialog.askopenfilename(
            title="Select a sample file",
            filetypes=[("Sample files", "*.zip")]
        )
        push_sample_window.lift()  # Re-lift after file dialog is opened
        push_sample_window.focus_force()  # Ensure window regains focus

        # Verify that a ZIP file is selected and exists
        if file_path and file_path.lower().endswith('.zip') and os.path.exists(file_path):
            lbl_sample_file.config(text="File opened: " + file_path)
            push_files = [file_path]
            multi_files = False
        else:
            push_files = []
            lbl_sample_file.config(text="No valid file selected.")
            if file_path and not file_path.lower().endswith('.zip'):
                messagebox.showerror("Error", "Selected file is not a ZIP file.")

    def push_sample_file():
        global selected_device, push_files, multi_files
        if not selected_device_serial:
            messagebox.showerror("Error", "Select a device first.")
            return
        
        selected_device = selected_device_serial

        if not push_files and not multi_files:
            messagebox.showerror("Error", "Select a sample file first.")
            return

        # Create the directory in case it doesn't exist.
        run_adb_command(["adb", "-s", selected_device_serial, "shell", "mkdir", "-p", "/sdcard/Android/data/org.emulator.arcade/files/samples"])

        # Check if the files exist
        for filePath in push_files:
            writeLog("Checking file ", filePath)
            if not os.path.exists(filePath):
                messagebox.showerror("Error", f"Sample file {filePath} does not exist.")
                return

        # Run adb root command
        adb_root_cmd = ["adb", "-s", selected_device, "root"]
        writeLog("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the sample files
        for filePath in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", filePath, "/sdcard/Android/data/org.emulator.arcade/files/samples/"]
            writeLog("Running ADB Command:", push_cmd)
            if run_adb_command(push_cmd) is None:
                messagebox.showerror("Error", f"Failed to push {filePath}.")
                return
        
        messagebox.showinfo("Success", "All samples pushed successfully.")

    # Use TkinterDnD.Toplevel for the new window
    push_sample_window = tk.Toplevel(root)
    push_sample_window.title("Push Sample")
    push_sample_window.lift()  # Ensure the window is above the main window
    push_sample_window.focus_force()  # Ensure the window gets focus

    # Bind focus events to keep the window on top
    push_sample_window.bind("<FocusIn>", lambda e: push_sample_window.lift())
    push_sample_window.bind("<Configure>", lambda e: push_sample_window.lift())

    tk.Button(push_sample_window, text="Select Sample", command=select_sample).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(push_sample_window, text="Push Sample", command=push_sample_file).grid(row=1, column=0, padx=10, pady=10)

    lbl_sample_file = tk.Label(push_sample_window, text="Select a sample file with the button above, or drag & drop here.")
    lbl_sample_file.grid(row=2, column=0, columnspan=1, padx=10, pady=10)

    def on_drag_enter(event):
        event.widget.focus_force()
        event.widget.config(relief="sunken")

    def on_drag_leave(event):
        event.widget.config(relief="raised")

    def on_drop(event):
        # Use regular expression to extract file paths
        files = re.findall(r'\{.*?\}|\S+', event.data)
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            multi_files = False
            # Remove curly braces if present
            cleaned_file = files[0].strip('{}')
            if os.path.exists(cleaned_file):
                push_files = [cleaned_file]  # Store as list
                lbl_sample_file.config(text=f"File opened: {cleaned_file}")
            else:
                lbl_sample_file.config(text="No valid file selected.")
                messagebox.showerror("Error", "Selected file does not exist.")
        else:
            multi_files = True
            valid_files = []
            for file in files:
                # Remove curly braces if present
                cleaned_file = file.strip('{}')
                if os.path.exists(cleaned_file):
                    valid_files.append(cleaned_file)
                else:
                    writeLog(f"File {cleaned_file} does not exist.")
                    messagebox.showerror("Error", f"File {cleaned_file} does not exist.")
            if valid_files:
                push_files = valid_files
                lbl_sample_file.config(text=f"{len(valid_files)} files loaded.")
            else:
                push_files = []
                lbl_sample_file.config(text="No valid file selected.")
                messagebox.showerror("Error", "No valid sample files were selected.")

        writeLog("Final list of files to push:", push_files)



    push_sample_window.drop_target_register(DND_FILES)
    push_sample_window.dnd_bind('<<DragEnter>>', on_drag_enter)
    push_sample_window.dnd_bind('<<DragLeave>>', on_drag_leave)
    push_sample_window.dnd_bind('<<Drop>>', on_drop)

def restart_launcher():
    if not selected_device_serial:
        messagebox.showwarning("Warning", "No device selected")
        return

    serial_number = selected_device_serial
    command = ["adb", "-s", serial_number, "shell", "am", "force-stop", "com.iircade.iiconsole"]
    run_adb_command(command)

# Developer Tools function
def developer_tools():
    if not selected_device_serial:
        messagebox.showerror("Error", "Select a device first.")
        return

    # Create the developer tools window
    developer_tools_window = tk.Toplevel(root)
    developer_tools_window.title("Developer Tools")

    # Function to handle enabling ADB over Wi-Fi temporarily
    def enable_adb_temp():
        if not selected_device_serial:
            messagebox.showwarning("Warning", "No device selected")
            return

        serial_number = selected_device_serial
        command = ["adb", "-s", serial_number, "tcpip", "5555"]
        if run_adb_command(command) == None:
            messagebox.showerror("Error", "Error enabling Wi-Fi debugging.")
        else:
            messagebox.showinfo("Success", "WI-Fi debugging temporarily enabled.")

    # Function to handle enabling ADB over Wi-Fi permanently
    def enable_adb_perm():
        selected_device = selected_device_serial
        pushError = False
        if run_adb_command(["adb", "-s", selected_device, "root"]) == None:
            pushError = True
        if not pushError:
            if run_adb_command(["adb", "-s", selected_device, "remount"]) == None:
                pushError = True
        if not pushError:
            push_cmd = ["adb", "-s", selected_device, "push", "adbtcp.rc", "/etc/init/"]
            writeLog("Running ADB Command:", push_cmd)
            if run_adb_command(push_cmd) == None:
                pushError = True
        if not pushError:
            if run_adb_command(["adb", "-s", selected_device, "reboot"]) == None:
                pushError = True
        if(pushError):
            messagebox.showerror("Error", "Enabling Wi-Fi debugging failed.")
        else:
            messagebox.showinfo("Success", "Wi-Fi debugging enabled permanently.\nBe aware that it can take your iiRcade\na few minutes after rebooting to\nreconnect to the network.")

    # Create buttons for developer tools
    btn_adb_temp = tk.Button(developer_tools_window, text="Enable ADB over Wi-Fi (Temporary)", command=enable_adb_temp)
    btn_adb_temp.pack(pady=10)

    btn_adb_perm = tk.Button(developer_tools_window, text="Enable ADB over Wi-Fi (Permanent)", command=enable_adb_perm)
    btn_adb_perm.pack(pady=10)

def on_listbox_select(event):
    global selected_device_serial
    if lb_devices.curselection():
        selected = lb_devices.get(lb_devices.curselection())
        selected_device_serial = selected
        current_device.config(text=selected)
    else:
        writeLog("No valid selection in listbox")

def run_adb_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            writeLog(f"ADB command {' '.join(command)} failed: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except Exception as e:
        writeLog(f"Failed to run adb command: {e}")
        return None


def populate_devices():
    """Runs `adb devices`, parses the output, and populates the listbox."""
    output = run_adb_command(["adb", "devices"])
    devices = []

    # Parse the output to extract device IDs
    for line in output.splitlines():
        if "\tdevice" in line:
            devices.append(line.split("\t")[0])

    # Clear the listbox and add devices
    lb_devices.delete(0, tk.END)
    for device in devices:
        lb_devices.insert(tk.END, device)

    # Schedule the next update
    root.after(5000, populate_devices)

# Create and place buttons
buttons = [
    ("Push CFG", push_cfg),
    ("Game Manager", game_manager),
    ("Fix Clock", fix_clock),
    ("Push Bezels", push_artwork),
    ("Reboot Cabinet", reboot_cabinet),
    ("Fix Licenses", fix_license),
    ("Push Sounds", push_sounds),
    ("Restart Launcher", restart_launcher),
    ("Developer Tools", developer_tools)
]

for i, (text, command) in enumerate(buttons):
    btn = tk.Button(root, text=text, command=command)
    btn.grid(row=i//3, column=i%3, padx=12, pady=10, sticky="nsew")

# Listbox for LBDevices
lb_devices = tk.Listbox(root, height=4)  # Adjust height as needed
lb_devices.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
lb_devices.bind("<<ListboxSelect>>", on_listbox_select)

# Frame to contain the labels
frame = tk.Frame(root)
frame.grid(row=3, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)

# Labels for Currently Selected Device
tk.Label(frame, text="Selected Device").pack(anchor="center")
current_device = tk.Label(frame, text="None")
current_device.pack(anchor="center")

# Populate devices on startup and schedule periodic updates
populate_devices()

# Start the main loop
root.mainloop()
