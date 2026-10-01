import serial
from tkinter import *
seri = serial.Serial(port='COM5', baudrate=9600 ) 
win = Tk()
win.title('[파이선] entry 제어')
win.config(bg="yellow")
def jang1():
    va11= e1.get()
    if va11== "led1on" :
       a='A' 
       a=a.encode() 
       print(a)  
       la1.config(text="첫번째ledon")
       seri.write(a)
    elif va11== "led1off" :
       a='B'
       a=a.encode()  
       print(a)  
       la1.config(text="첫번째ledoff")
       seri.write(a)
    elif va11=="led2on":
       a='C'
       a=a.encode() 
       print(a)   
       la2.config(text="두번째ledon")
       seri.write(a)
    elif va11=="led2off":
       a='D' 
       a=a.encode()  
       print(a)  
       la2.config(text="두번째ledoff")
       seri.write(a)
    else:
       la1.config(text="입력오류입니다")

e1=Entry(win,width=40,fg="green")
e1.config(bg="pink",font="16")
e1.grid(row=0,sticky=W+S+N+E)
la1=Label(win, text="led1결과표시",width=20,fg="green",bg="#ff0000",font="16")
la1.grid( row=1,sticky=W+S+N+E )
la2=Label(win, text="led2결과표시",width=20,fg="green",bg="#ff0000",font="16")
la2.grid( row=2,sticky=W+S+N+E)
bu1=Button(win, text='led선택버튼', bg="green",font="16",command=jang1)
bu1.grid(row=3,sticky=W+S+E)

win.geometry("280x200")
win.mainloop()

