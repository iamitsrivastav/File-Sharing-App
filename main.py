import http.server
import socket
import socketserver
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import threading
import pyqrcode

# Function to get the desktop path
def get_desktop_path():
    return os.path.join(os.path.join(os.environ['USERPROFILE']), 'OneDrive')

# Function to get the IP address
def get_ip_address():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

# Function to generate a more attractive QR code
def generate_qr_code(link, filename="myqr.png"):
    qr = pyqrcode.create(link)
    qr.png(filename, scale=8, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff])

    # Adding rounded corners to QR code image
    image = Image.open(filename).convert("RGBA")
    width, height = image.size

    # Create a rounded mask
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width, height), radius=50, fill=255)

    image.putalpha(mask)
    image.save(filename)

# Function to start the HTTP server
def start_http_server(port, handler, ip):
    global httpd
    httpd = socketserver.TCPServer(("", port), handler)
    print(f"Serving at port {port}")
    print(f"Type this in your browser: {ip}")
    print("or use the QR code")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    finally:
        httpd.server_close()

# Function to handle start server button click
def on_start_server():
    global qr_code_img

    desktop_path = get_desktop_path()
    os.chdir(desktop_path)
    
    Handler = http.server.SimpleHTTPRequestHandler
    ip_address = get_ip_address()
    ip = f"http://{ip_address}:{PORT}"

    generate_qr_code(ip)
    
    qr_code_img = ImageTk.PhotoImage(Image.open("myqr.png"))

    qr_label.config(image=qr_code_img)
    qr_text_label.config(text="Scan the QR")
    
    server_thread = threading.Thread(target=start_http_server, args=(PORT, Handler, ip))
    server_thread.daemon = True
    server_thread.start()

# Function to handle stop server button click
def on_stop_server():
    global httpd
    if httpd:
        httpd.shutdown()
        messagebox.showinfo("Server Stopped", "The HTTP server has been stopped.")
        qr_label.config(image='')
        qr_text_label.config(text="For QR click on Start Server button")

# Function to change button color on click
def change_color(button, color):
    button.config(bg=color)

# Function to create round-shaped buttons using canvas
def create_round_button(canvas, x, y, text, command, bg_color, fg_color, active_bg_color):
    r = 40  # Radius of the circle
    id1 = canvas.create_oval(x-r, y-r, x+r, y+r, fill=bg_color, outline="")
    
    button = tk.Button(canvas, text=text, command=command, font=("Helvetica", 10), bg=bg_color, fg=fg_color, 
                       relief="flat", highlightthickness=0, activebackground=active_bg_color, cursor="hand2")
    
    button_window = canvas.create_window(x, y, window=button, width=2*r-10, height=2*r-10)

    def on_enter(e):
        canvas.itemconfig(id1, fill=active_bg_color)
    
    def on_leave(e):
        canvas.itemconfig(id1, fill=bg_color)
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    
    return button

if __name__ == "__main__":
    PORT = 8010

    app = tk.Tk()
    app.title("HTTP Server with QR Code")
    app.geometry("500x600")

    # Load and display the image
    image = Image.open("file.jpeg")  # Replace with your image path
    image = image.resize((100, 100), Image.LANCZOS)
    img = ImageTk.PhotoImage(image)
    img_label = tk.Label(app, image=img)
    img_label.pack(pady=10)

    canvas = tk.Canvas(app, width=500, height=100, bg="white")
    canvas.pack()

    start_button = create_round_button(canvas, 150, 50, "Start Server", on_start_server, "green", "white", "darkgreen")
    stop_button = create_round_button(canvas, 350, 50, "Stop Server", on_stop_server, "red", "white", "darkred")
    
    qr_text_label = tk.Label(app, text="For QR click on Start Server button", font=("Helvetica", 16))
    qr_text_label.pack(pady=10)
    
    qr_label = tk.Label(app)
    qr_label.pack(pady=20)

    app.mainloop()
