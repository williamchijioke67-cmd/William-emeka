import tkinter

button_values = [
    ["AC", "+/-", "%", "+"],
    ["7", "8", "9", "-"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "+"],
    ["0", ".", "=", "÷"]
]

right_symbols = ["÷", "×", "-", "+", "="]
top_symbols = ["AC", "+/-", "%"]

row_count = len(button_values) #5
column_count = len(button_values[0]) #4

color_light_gray = "#D3D3D3"
color_black = "#000000"
color_dark_gray = "#A9A9A9"
color_white = "white"
color_orange = "#FFA500"
 
#window setup 
window = tkinter.Tk()
window.title("Calculator")
window.resizable(False, False)

frame = tkinter.Frame(window)
label = tkinter.Label(frame, text="0", font=("Arial", 30), background=color_black,
                      foreground=color_white, anchor="e", width=column_count)

label.grid(row=0, column=0, columnspan=column_count, sticky="we")

for row in range(row_count):
    for column in range(column_count):
        value = button_values[row][column]
        button = tkinter.Button(frame, text=value, font=("Arial", 30),
                                width=column_count-1, height=1,
                                command=lambda value=value: button_clicked(value))

        if value in top_symbols:
            button.config(foreground=color_black,background=color_light_gray)
        elif value in right_symbols:
            button.config(foreground=color_white, background=color_orange)
        else:
            button.config(foreground=color_white, background=color_dark_gray)

        button.grid(row=row+1, column=column)



        button.grid(row=row+1, column=column)

frame.pack()

#A+B, A-B, A*B, A/B
A = "0"
operator = None
B = None

def clear_all():
    global A, B, operator
    A = "0"
    operator = None
    B = None

def remove_zero_decimal(value):
    if value % 1 == 0:
        value = int(value)
    return str(value)

def button_clicked(value):
    global A, B, operator

    if value in right_symbols:

        if value == "=":
            if A is not None and operator is not None:

                B = label["text"]

                numA = float(A)
                numB = float(B)

                if operator == "+":
                    result = numA + numB
                elif operator == "-":
                    result = numA - numB
                elif operator == "×":
                    result = numA * numB
                elif operator == "÷":
                    if numB == 0:
                        label["text"] = "Error"
                        clear_all()
                        return
                    result = numA / numB

                label["text"] = remove_zero_decimal(result)

                A = label["text"]
                B = None
                operator = None

        else:
            A = label["text"]
            operator = value
            label["text"] = "0"

    elif value in top_symbols:

        if value == "AC":
            clear_all()
            label["text"] = "0"

        elif value == "+/-":
            result = float(label["text"]) * -1
            label["text"] = remove_zero_decimal(result)

        elif value == "%":
            result = float(label["text"]) / 100
            label["text"] = remove_zero_decimal(result)

    else:

        if value == ".":
            if "." not in label["text"]:
                label["text"] += "."

        elif value in "0123456789":
            if label["text"] == "0":
                label["text"] = value
            else:
                label["text"] += value

                
#center the window
window.update()
window_width = window.winfo_width()
window_height = window.winfo_height()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window_x = int((screen_width/2) - (window_width/2))
window_y = int((screen_height/2) - (window_height/2))

#front "(w)x(h)+(x)+(y)"
window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()