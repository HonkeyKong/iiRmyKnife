import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import os, subprocess
from datetime import datetime
from tkinterdnd2 import DND_FILES, TkinterDnD

# Initialize the main window
# Load the tkdnd library
root = TkinterDnD.Tk()

root.title("iRmyKnife v0.1 by HonkeyKong")

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

    def validate_cfg(file_path):
        xsd_data = """
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">

            <xs:element name="mameconfig">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="system" type="SystemType"/>
                    </xs:sequence>
                    <xs:attribute name="version" type="xs:string" use="required"/>
                </xs:complexType>
            </xs:element>

            <xs:complexType name="SystemType">
                <xs:sequence>
                    <xs:choice maxOccurs="unbounded">
                        <xs:element name="input" type="InputType"/>
                        <xs:element name="crosshairs" type="CrosshairsType" minOccurs="0"/>
                        <xs:element name="ui_warnings" type="UiWarningsType" minOccurs="0"/>
                    </xs:choice>
                </xs:sequence>
                <xs:attribute name="name" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="InputType">
                <xs:sequence>
                    <xs:element name="port" type="PortType" maxOccurs="unbounded"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="PortType">
                <xs:sequence>
                    <xs:element name="newseq" type="NewSeqType" minOccurs="0" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:attribute name="tag" type="xs:string" use="required"/>
                <xs:attribute name="type" type="xs:string" use="required"/>
                <xs:attribute name="mask" type="xs:string" use="required"/>
                <xs:attribute name="defvalue" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="NewSeqType">
                <xs:simpleContent>
                    <xs:extension base="xs:string">
                        <xs:attribute name="type" type="xs:string" use="required"/>
                    </xs:extension>
                </xs:simpleContent>
            </xs:complexType>

            <xs:complexType name="CrosshairsType">
                <xs:sequence>
                    <xs:element name="crosshair" type="CrosshairType" maxOccurs="unbounded"/>
                </xs:sequence>
            </xs:complexType>

            <xs:complexType name="CrosshairType">
                <xs:attribute name="player" type="xs:string" use="required"/>
                <xs:attribute name="mode" type="xs:string" use="required"/>
            </xs:complexType>

            <xs:complexType name="UiWarningsType">
                <xs:sequence>
                    <xs:element name="feature" type="FeatureType" maxOccurs="unbounded"/>
                </xs:sequence>
                <xs:attribute name="launched" type="xs:string" use="optional"/>
                <xs:attribute name="warned" type="xs:string" use="optional"/>
            </xs:complexType>

            <xs:complexType name="FeatureType">
                <xs:attribute name="device" type="xs:string" use="required"/>
                <xs:attribute name="type" type="xs:string" use="required"/>
                <xs:attribute name="status" type="xs:string" use="required"/>
            </xs:complexType>

        </xs:schema>
        """
        try:
            from lxml import etree
            schema_root = etree.XML(xsd_data)
            schema = etree.XMLSchema(schema_root)
            parser = etree.XMLParser(schema=schema)
            
            # Read/print the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                # print("File Content:\n", file_content)  # Debugging line
                etree.fromstring(file_content, parser)
            
            return True
        except Exception as ex:
            messagebox.showerror("Error", f"Validation failed: {ex}")
            print(f"Validation failed: {ex}")
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
        # print("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the CFG files
        pushError = False
        for file_path in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", file_path, "/sdcard/Android/data/org.emulator.arcade/files/cfg/"]
            # print("Running ADB Command:", push_cmd)
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
        # print("Running ADB Command:", lg_push_cmd)
        if run_adb_command(lg_push_cmd) == None:
            pushError = True
        if(pushError):
            messagebox.showerror("Error", "Error setting up light gun.")
            return
        
        db_loc = "/data/data/com.iircade.iiconsole/databases/Game.db"
        db_update_cmd = "\"update GAME set Reserve1='T#0#1' where GAME.ID='{rom_name}.zip';\""
        db_exec_cmd = ["adb", "-s", selected_device, "shell", "sqlite3", db_loc, db_update_cmd]
        # print("Running ADB Command:", db_exec_cmd)
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
        files = event.data.split()
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            if validate_cfg(files[0]):
                multi_files = False
                push_files = [files[0]]
                lbl_cfg_file.config(text=f"File opened: {files[0]}")
        else:
            multi_files = True
            valid_files = []
            for file in files:
                if os.path.exists(file) and validate_cfg(file):
                    valid_files.append(file)
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
        db_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, f"\"DELETE FROM GAME WHERE ID='{game_id}';\""]
        config_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, f"\"DELETE FROM CONFIG WHERE ID='{game_id}';\""]
        
        if run_adb_command(db_command) is None:
            errorString = "Failed to delete from GAME database."
            pushError = True
        if run_adb_command(config_command) is None:
            errorString = "Failed to delete from CONFIG database."
            pushError = True
        if(pushError):
            messagebox.showerror("Error", errorString)
            return
        
        if game_id.endswith(".zip"):  # MAME ROM
            remove_command = ["adb", "-s", selected_device, "shell", "rm", f"{GAME_FOLDER_PATH}/{game_id}"]
            if run_adb_command(remove_command) is not None:
                messagebox.showinfo("Success", f"MAME ROM {game_id} uninstalled.")
        else:  # Android application
            uninstall_command = ["adb", "-s", selected_device, "uninstall", game_id]
            if run_adb_command(uninstall_command) is not None:
                messagebox.showinfo("Success", f"Android app {game_id} uninstalled.")

    def list_installed_games():
        query_command = ["adb", "-s", selected_device, "shell", "sqlite3", DATABASE_PATH, "\"SELECT * FROM GAME;\""]
        output = run_adb_command(query_command)
        if output:
            games = output.split('\n')
            game_listbox.delete(0, tk.END)
            for game in games:
                details = game.split('|')
                if len(details) >= 4:  # Ensure there are enough elements
                    game_number = details[0]
                    game_id = details[1]
                    game_name = details[3]
                    game_listbox.insert(tk.END, f"Number: {game_number}, ID: {game_id}, Name: {game_name}")
                else:
                    print(f"Unexpected game format: {game}")  # Log unexpected formats

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

    # Create a listbox to display the list of games
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
        for file_path in push_files:
            # print("Checking file ", file_path)
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"Bezel file {file_path} does not exist.")
                return

        # Run adb root command
        adb_root_cmd = ["adb", "-s", selected_device, "root"]
        # print("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the artwork files
        for file_path in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", file_path, "/sdcard/Android/data/org.emulator.arcade/files/artwork/"]
            # print("Running ADB Command:", push_cmd)
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
        files = event.data.split()
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            multi_files = False
            push_files = [files[0]]  # Store as list
            lbl_artwork_file.config(text=f"File opened: {files[0]}")
        else:
            multi_files = True
            for file in files:
                if os.path.exists(file):
                    push_files.append(file)
            lbl_artwork_file.config(text=f"{len(files)} files loaded.")

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

    # print("Running ADB Command:", db_exec_cmd)  # Print for debugging
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
            # print("Checking file ", filePath)
            if not os.path.exists(filePath):
                messagebox.showerror("Error", f"Sample file {filePath} does not exist.")
                return

        # Run adb root command
        adb_root_cmd = ["adb", "-s", selected_device, "root"]
        # print("Running ADB Command:", adb_root_cmd)
        run_adb_command(adb_root_cmd)

        # Push the sample files
        for filePath in push_files:
            push_cmd = ["adb", "-s", selected_device, "push", filePath, "/sdcard/Android/data/org.emulator.arcade/files/samples/"]
            # print("Running ADB Command:", push_cmd)
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
        files = event.data.split()
        global push_files, multi_files
        push_files = []
        if len(files) == 1:
            multi_files = False
            push_files = [files[0]]
            lbl_sample_file.config(text=f"File opened: {files[0]}")
        else:
            multi_files = True
            for file in files:
                if os.path.exists(file):
                    push_files += [file]
            lbl_sample_file.config(text=f"{len(files)} files loaded.")

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
            # print("Running ADB Command:", push_cmd)
            if run_adb_command(push_cmd) == None:
                pushError = True
        if not pushError:
            if run_adb_command(["adb", "-s", selected_device, "reboot"]) == None:
                pushError = True
        if(pushError):
            messagebox.showerror("Error", "Enabling Wi-Fi debugging failed.")
        else:
            messagebox.showinfo("Success", "Wi-Fi debugging enabled permanently.")

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
        print("No valid selection in listbox")

def run_adb_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr)
        return result.stdout
    except Exception as e:
        messagebox.showerror("Error", f"ADB command {' '.join(command)} failed: {e}")
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
    btn.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")

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