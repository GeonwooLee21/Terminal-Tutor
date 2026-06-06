# Terminal Keypad - main.py
import os
import subprocess

from rich.console import Console
from rich.table import Table

console = Console()

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

def get_arg_buttons(command, state):
    entries = os.listdir(state["current_dir"])

    if command == "cd":
        folders = [e for e in entries if os.path.isdir(os.path.join(state["current_dir"], e))]
        targets = ["..", "."] + sorted(folders)
    else:
        targets = sorted(entries)

    return [Button(label=t, command=f"{command} {t}") for t in targets]

def show_keypad(buttons, state):
    console.print(f"\n 📁 현재 위치: [bold cyan]{state['current_dir']}[/bold cyan]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column()
    table.add_column()
    table.add_column()

    # 버튼 3개씩 묶어서 행으로 추가
    row = []
    for i, btn in enumerate(buttons):
        label = f"[{i+1}] {btn.label}"
        if btn.dangerous:
            row.append(f"[bold red]{label}[/bold red]")
        else:
            row.append(label)

        if len(row) == 3:
            table.add_row(*row)
            row = []

    # 남은 버튼 처리 (버튼 수가 3의 배수가 아닐 때)
    if row:
        while len(row) < 3:
            row.append("")
        table.add_row(*row)

    console.print(table)
    console.print("─" * 40)

ARG_PROMPTS = {
    "mkdir": "생성할 폴더명을 입력하세요",
    "touch": "생성할 파일명을 입력하세요",
}

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
        if not (0 <= index < len(keypad_buttons)):
            print("없는 번호입니다.")
            continue

        btn = keypad_buttons[index]

        # 인자 후보가 있는 명령어: 화면 전환
        if btn.command in ["cd", "cat", "rm", "rm -rf"]:
            arg_buttons = get_arg_buttons(btn.command, state)

            if not arg_buttons:
                # 후보가 없을 때 (빈 디렉토리 등)
                print("선택 가능한 항목이 없습니다.")
                continue

            # 인자 선택 화면으로 전환
            show_keypad(arg_buttons, state)
            arg_choice = input("번호를 입력하세요 [b: 뒤로]: ").strip()

            if arg_choice == 'b':
                continue

            if not arg_choice.isdigit():
                print("숫자를 입력해주세요.")
                continue

            arg_index = int(arg_choice) - 1
            if not (0 <= arg_index < len(arg_buttons)):
                print("없는 번호입니다.")
                continue

            selected = arg_buttons[arg_index]

            if btn.command == "cd":
                try:
                    os.chdir(selected.label)
                    state["current_dir"] = os.getcwd()
                    result = f"✅ {state['current_dir']} 로 이동했습니다."
                except FileNotFoundError:
                    result = f"❌ '{selected.label}' 폴더를 찾을 수 없습니다."
            else:
                result = selected.execute(state)

        # mkdir, touch
        elif btn.command in ["mkdir", "touch"]:
            prompt = ARG_PROMPTS[btn.command]
            arg = input(f"{prompt} [b: 뒤로]: ").strip()
            if arg == 'b':
                continue
            temp_btn = Button(btn.label, f"{btn.command} {arg}", btn.dangerous)
            result = temp_btn.execute(state)

        else:
            result = btn.execute(state)

        if result:
            print(result)

if __name__ == "__main__":
    main()