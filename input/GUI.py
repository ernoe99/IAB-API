import tkinter as tk

hpvalid_str = ['FM_HP_1_mTT_dp', 'FM_HP_2a_mTT_dp', 'FM_HP_1_oTT_dp']

root = tk.Tk()
root.geometry('500x500')
dropdown_var = tk.StringVar()
dropdown_var.set(hpvalid_str[0])

show_label_var = tk.StringVar()
show_label_var.set('None')

dropdown = tk.OptionMenu(root, dropdown_var, *hpvalid_str)
dropdown.pack()


def get_value(*args):
    show_label_var.set(f"Submission is: {dropdown_var.get()}")
    print(dropdown_var.get())



#
#
# dropdown_var.trace('w', get_value)
# button = tk.Button(root, text='Get Value', command=get_value)
# button.pack()

x = dropdown_var.get()
print("ooo", x)
dropdown_var.trace('w', get_value)


label = tk.Label(root, textvariable=show_label_var)
label.pack(side="bottom")

root.mainloop()

