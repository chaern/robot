import serial
from tkinter import *

seri = serial.Serial(port="COM5", baudrate=9600)
win = Tk()
win.title("[파이선] 체크박스 LED 제어")
win.config(bg="yellow")


chk1=IntVar()
chk2=IntVar()


def jang1(led):
   if led == 1:
      if chk1.get():
         command = b"A"
         la1.config(text="첫번째 LED 켜짐")
      else:
         command = b"B"
         la1.config(text="첫번째 LED 꺼짐")
   elif chk2.get():
      command = b"C"
      la2.config(text="두번째 LED 켜짐")
   else:
      command = b"D"
      la2.config(text="두번째 LED 꺼짐")

   print(command)
   seri.write(command)


bt1 = Checkbutton(
   win, text="LED 1", variable=chk1, command=lambda: jang1(1), bg="yellow"
)
bt1.grid(column=0, row=0)
bt2 = Checkbutton(
   win, text="LED 2", variable=chk2, command=lambda: jang1(2), bg="yellow"
)
bt2.grid(column=0, row=1)

la1 = Label(
   win, text="첫번째 LED 결과 표시", width=20, height=2, fg="green", bg="#ff0000"
)
la1.grid(column=0, row=2)
la2 = Label(
   win, text="두번째 LED 결과 표시", width=20, height=2, fg="green", bg="yellow"
)
la2.grid(column=0, row=3)


win.mainloop()

