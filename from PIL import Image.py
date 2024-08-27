import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk, messagebox
import socket
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os

# Common ports and their associated services
common_ports = {
    20: "FTP (File Transfer Protocol)",
    21: "FTP (File Transfer Protocol)",
    22: "SSH (Secure Shell)",
    23: "Telnet",
    25: "SMTP (Simple Mail Transfer Protocol)",
    53: "DNS (Domain Name System)",
    80: "HTTP (Hypertext Transfer Protocol)",
    110: "POP3 (Post Office Protocol)",
    143: "IMAP (Internet Message Access Protocol)",
    443: "HTTPS (HTTP Secure)",
    3306: "MySQL",
    3389: "RDP (Remote Desktop Protocol)",
    5900: "VNC (Virtual Network Computing)",
    8080: "HTTP (Alternative Port)",
}

# Function to scan a single port
def scan_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
        except (socket.timeout, socket.error):
            return False
        else:
            return True

# Function to scan a range of ports
def scan_ports():
    host = host_entry.get()
    start_port = int(start_port_entry.get())
    end_port = int(end_port_entry.get())
    
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"Scanning ports {start_port} to {end_port} on {host}...\n")
    progress_bar['value'] = 0
    open_ports = []

    total_ports = end_port - start_port + 1
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(scan_port, host, port) for port in range(start_port, end_port + 1)]
        for i, (port, future) in enumerate(zip(range(start_port, end_port + 1), futures)):
            progress_bar['value'] = (i + 1) / total_ports * 100
            root.update_idletasks()
            if future.result():
                open_ports.append(port)

    if open_ports:
        output_text.insert(tk.END, "Open ports:\n")
        for port in open_ports:
            service = common_ports.get(port, "Unknown Service")
            output_text.insert(tk.END, f"Port {port} is open ({service})\n")
    else:
        output_text.insert(tk.END, "No open ports found\n")

    save_button.config(state=tk.NORMAL)

# Function to save the scan results to a file
def save_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w') as file:
            file.write(output_text.get(1.0, tk.END))
        messagebox.showinfo("Save Results", f"Results saved to {file_path}")

# Function to change theme
def change_theme(theme):
    style.theme_use(theme)

# Function to connect to VPN
def connect_vpn():
    vpn_config = vpn_entry.get()
    if vpn_config:
        try:
            subprocess.run(["sudo", "openvpn", "--config", vpn_config], check=True)
            messagebox.showinfo("VPN Connection", "Connected to VPN successfully!")
        except subprocess.CalledProcessError:
            messagebox.showerror("VPN Connection", "Failed to connect to VPN. Please check the configuration.")
    else:
        messagebox.showwarning("VPN Connection", "Please provide a VPN configuration file.")

# Function to show information about the tool
def show_info():
    info_text = (
        "Enhanced Port Scanner Tool with VPN Option\n"
        "Version: 1.1\n\n"
        "Features:\n"
        "- Scan a range of ports on a specified host\n"
        "- Save scan results to a text file\n"
        "- Connect to a VPN using a configuration file\n"
        "- Display information about common ports and their services\n"
        "- Change the theme of the interface\n\n"
        "How to use:\n"
        "1. Enter the host IP or domain.\n"
        "2. Specify the range of ports to scan.\n"
        "3. (Optional) Connect to a VPN using a valid .ovpn file.\n"
        "4. Click 'Scan Ports' to start scanning.\n"
        "5. Save the results using the 'Save Results' button.\n\n"
        "Developed by: Your Name"
    )
    messagebox.showinfo("Application Info", info_text)

# Create the main window
root = tk.Tk()
root.title("Enhanced Port Scanner with VPN and Port Info")
root.geometry("600x600")

# Apply a theme to the interface
style = ttk.Style(root)
themes = style.theme_names()
style.theme_use(themes[0])

# Create and place the widgets
tk.Label(root, text="Host (IP or domain):").grid(row=0, column=0, padx=10, pady=5, sticky='e')
host_entry = tk.Entry(root, width=30)
host_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
host_entry.insert(0, "127.0.0.1")

tk.Label(root, text="Start Port:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
start_port_entry = tk.Entry(root, width=30)
start_port_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
start_port_entry.insert(0, "1")

tk.Label(root, text="End Port:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
end_port_entry = tk.Entry(root, width=30)
end_port_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
end_port_entry.insert(0, "1024")

scan_button = tk.Button(root, text="Scan Ports", command=scan_ports)
scan_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

save_button = tk.Button(root, text="Save Results", command=save_results, state=tk.DISABLED)
save_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, length=500, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

output_text = scrolledtext.ScrolledText(root, width=60, height=20)
output_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# VPN connection section
tk.Label(root, text="VPN Config File:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
vpn_entry = tk.Entry(root, width=30)
vpn_entry.grid(row=6, column=1, padx=10, pady=5, sticky='w')
vpn_entry.insert(0, "/path/to/vpn/config.ovpn")

vpn_button = tk.Button(root, text="Connect VPN", command=connect_vpn)
vpn_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# Show Info button
info_button = tk.Button(root, text="Show Info", command=show_info)
info_button.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Theme selection dropdown
theme_label = tk.Label(root, text="Select Theme:")
theme_label.grid(row=9, column=0, padx=10, pady=5, sticky='e')
theme_dropdown = ttk.Combobox(root, values=themes)
theme_dropdown.current(themes.index(themes[0]))
theme_dropdown.grid(row=9, column=1, padx=10, pady=5, sticky='w')
theme_dropdown.bind("<<ComboboxSelected>>", lambda e: change_theme(theme_dropdown.get()))

# Exit button
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.grid(row=10, column=0, columnspan=2, pady=10)

# Add tooltips
def add_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry("+0+0")
    label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1)
    label.pack(ipadx=1)
    tooltip.withdraw()

    def on_enter(event):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        tooltip.wm_geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def on_leave(event):
        tooltip.withdraw()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

add_tooltip(scan_button, "Click to scan the specified ports.")
add_tooltip(save_button, "Click to save the scan results to a file.")
add_tooltip(vpn_button, "Click to connect to the VPN using the specified configuration file.")
add_tooltip(info_button, "Click to view detailed information about the tool.")

# Start the GUI event loop
root.mainloop()

