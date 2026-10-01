import serial
import tkinter as tk
from tkinter import messagebox


def open_serial(port_name="COM5", baudrate=9600):
    try:
        return serial.Serial(port=port_name, baudrate=baudrate, timeout=1)
    except serial.SerialException as e:
        messagebox.showerror(
            "시리얼 연결 오류",
            f"{port_name} 포트를 열 수 없습니다.\n"
            "아두이노가 연결되어 있는지 확인하고 포트명을 다시 확인하세요.\n"
            f"오류: {e}",
        )
        return None


# 아두이노 시리얼 연결
seri = open_serial()

# Tkinter 창 생성
win = tk.Tk()
win.title("[파이썬] 버튼 LED 제어")
win.config(bg="yellow")


class LedControl:
    def __init__(self, win, seri):
        self.win = win
        self.seri = seri
        self.serial_ready = self.seri is not None and self.seri.is_open

        # 버튼 명령
        self.commands = ["ON", "OFF", "BLINKING"]

        # 버튼 생성
        for i, comm in enumerate(self.commands):
            bt = tk.Button(
                self.win,
                text=comm,
                width=20,
                height=5,
                bg="gray",
                fg="black",
                command=lambda cmd=comm: self.button_click(cmd),
                state="normal" if self.serial_ready else "disabled",
            )

            bt.grid(column=i, row=0, padx=5, pady=5)

        if not self.serial_ready:
            tk.Label(
                self.win,
                text="시리얼 연결이 없습니다. Arduino를 연결한 뒤 다시 실행하세요.",
                bg="yellow",
                fg="red",
                font=("Arial", 11, "bold"),
            ).grid(column=0, row=1, columnspan=3, pady=10)

    # 버튼 클릭 함수
    def button_click(self, value):
        if self.seri is None or not self.seri.is_open:
            messagebox.showwarning("시리얼 상태", "아두이노 연결이 없습니다.")
            return

        print("버튼 :", value)

        if value == "ON":
            send_data = "A"
        elif value == "OFF":
            send_data = "B"
        elif value == "BLINKING":
            send_data = "C"
        else:
            return

        # 문자열 -> bytes 변환
        send_byte = send_data.encode()

        # 아두이노로 전송
        self.seri.write(send_byte)
        print("전송 데이터 :", send_data)


# 객체 생성
btn = LedControl(win, seri)


def on_close():
    if seri is not None and seri.is_open:
        seri.close()
    win.destroy()


win.protocol("WM_DELETE_WINDOW", on_close)

# GUI 실행
win.mainloop()