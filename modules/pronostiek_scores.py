import tkinter as tk

# Venster maken
root = tk.Tk()
root.title("Test labels")
root.geometry("300x150")

# Eerste label
label1 = tk.Label(root, text="Dit is label 1")
label1.pack(pady=10)

# Tweede label
label2 = tk.Label(root, text="Dit is label 2")
label2.pack(pady=10)

# Programma starten
root.mainloop()
