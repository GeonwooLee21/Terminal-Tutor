# Terminal Keypad - main.py
import os
import subprocess

state = {
    "current_dir": os.getcwd(), # 현재 경로
    "last_output": "",          # 마지막 명령어 출력
    "warning_mode": True        # 위험 명령어 경고
}

class Button:
    def __init__(self, label, command, dangerous=False):
        self.label = label # label: 버튼에 표시될 이름 (예: "ls")
        self.command = command # command: 실행할 터미널 명령어 (예: "ls") 
        self.dangerous = dangerous # dangerous: 위험한 명령어 여부 (True면 경고 표시)

    def execute(self, state):
        # 1. self.dangerous가 True면 warn_user()를 호출
        if self.dangerous:
            if not warn_user(self):
                return

        # 2. subprocess로 self.command를 실행 
        result = subprocess.run(
            self.command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=state["current_dir"]
        )
        
        # 3. 실행 결과를 state에 저장 (출력 없으면 에러 메시지 저장)
        state["last_output"] = result.stdout or result.stderr

        # 4. 실행 결과 반환
        return state["last_output"]

def warn_user(button):
    # 1. 위험 경고 메시지를 출력
    print(f"⚠️  '{button.command}' 는 위험한 명령어입니다!")

    while True:
        # 2. 사용자에게 y/n 입력을 받음
        answer = input("실행하시겠습니까? [y/n]: ").strip()

        # 3. y면 True, n이면 False를 반환
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("잘못된 입력입니다.")
            continue

def change_directory(state):
    # 1. 이동할 폴더 이름을 입력받음
    target = input("이동할 폴더 이름 입력: ").strip()

    try:
        # 2. os.chdir()로 이동을 시도
        os.chdir(target)
        # 3. 성공하면 state의 경로를 새 경로로 업데이트
        state["current_dir"] = os.getcwd()
        return f"✅ {state['current_dir']} 로 이동했습니다."
    except FileNotFoundError:
        # 4. 실패하면 오류 메시지를 반환 및 기존 경로 유지
        return f"❌ '{target}' 폴더를 찾을 수 없습니다."

keypad_buttons = [
    # 탐색 (Navigation)
    Button(label='ls', command='ls'),
    Button(label='pwd', command='pwd'),
    Button(label='cd', command='cd'),

    # 생성 (Create)
    Button(label='mkdir', command='mkdir'),
    Button(label='touch', command='touch'),

    # 확인 (Inspect)
    Button(label='cat', command='cat'),
    Button(label='clear', command='clear'),

    # 삭제 (Delete) [dangerous=True]
    Button(label='rm',    command='rm',    dangerous=True),
    Button(label='rm -rf',command='rm -rf',dangerous=True)
]

def show_keypad(buttons, state):
    # 현재 경로 표시
    print("=" * 60)
    print(f" 📁 현재 위치: {state['current_dir']}")
    print("=" * 60)

    # 버튼을 번호와 함께 출력 (3열 배치)
    for i, btn in enumerate(buttons):
        number = f"[{i + 1}]"
        label = btn.label
        print(f"  {number:<5} {label:<10}", end="")
        # 3개마다 줄바꿈
        if (i + 1) % 3 == 0:
            print()

    print()  # 마지막 줄 정리
    print("=" * 60)

def main():
    while True:
        show_keypad(keypad_buttons, state)
        choice = input("번호를 입력하세요 [q: 종료]: ").strip()

        if choice == 'q':
            print("종료합니다.")
            break

        if not choice.isdigit():
            print("숫자를 입력해주세요.")
            continue

        index = int(choice) - 1
        if 0 <= index < len(keypad_buttons):
            btn = keypad_buttons[index]

            # cd 버튼은 change_directory()로 분기
            if btn.command == "cd":
                result = change_directory(state)

            # 인자가 필요한 명령어는 추가 입력을 받아서 붙임
            elif btn.command in ["mkdir", "touch", "cat", "rm", "rm -rf"]:
                arg = input(f"'{btn.label}' 대상 입력: ").strip()
                temp_btn = Button(btn.label, f"{btn.command} {arg}", btn.dangerous)
                result = temp_btn.execute(state)

            # 나머지는 그냥 execute()
            else:
                result = btn.execute(state)

            if result:
                print(result)
        else:
            print("없는 번호입니다.")

if __name__ == "__main__":
    main()