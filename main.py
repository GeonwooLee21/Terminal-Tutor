# Terminal Keypad - main.py
import os
import subprocess

from rich.console import Console
from rich.table import Table
from rich.rule import Rule # By Claude : UI에서의 가변 길이 선

console = Console()

state = {
    "mode": "",                 # 현재 모드 (튜토리얼 후 "beginner" 또는 "expert"로 설정됨)
    "show_command": False,      # 명령어명 토글 상태
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


# 1. "터미널을 처음 사용해 보시나요? [Y/N]" 출력
# 2. Y 입력 시:
#    - 환영 메시지 출력
#    - state["mode"] = "beginner" 로 설정
# 3. N 입력 시:
#    - "Terminal Keypad는 터미널이 낯선 분들을 위해..." 메시지 출력
#    - "그래도 한번 둘러보시겠습니까? [Y/N]" 출력
#    - Y → state["mode"] = "expert"
#    - N → 프로그램 종료
# 4. Y/N 외 입력 시 다시 물어봄 (warn_user처럼 while True 루프)
def onboarding():
    while True:
        # 2. 사용자에게 y/n 입력을 받음
        answer = input("터미널을 처음 사용해 보시나요? [y/n]: ").strip()

        # 3. y면 True, n이면 False를 반환
        if answer == "y":
            state["mode"] = "beginner"
            input(f"환영합니다. Terminal Keypad는 사용자님이 터미널 환경에 익숙해질 수 있도록 도움을 주는 프로그램입니다.\n"
                  f"본 프로그램에서 제공되는 터미널 명령어들을 통해 터미널에 익숙해지세요.\n"
                  f"그리고 터미널에 익숙해 졌다면 저에게 말씀해 주세요! [Enter]\n")
            print("\033[2J\033[3J\033[H", end="") # By Claude : macOS 터미널에서 clear는 화면을 밀어올릴 뿐, 스크롤 버퍼를 지우지 않음. 버퍼까지 지우려면 ANSI 이스케이프 코드를 직접 출력해야 함.
            return True
        elif answer == "n":
            while True:
                answer = input(f"Terminal Keypad는 터미널 환경이 낯선 분들을 위해 설계된 프로그램입니다.\n"
                               f"터미널에 이미 익숙하시다면 기존 터미널 환경이 더 편하실 수도 있습니다.\n"
                               f"그래도 한번 둘러보시겠습니까? [y/n]\n").strip()
                if answer == "y":
                    state["mode"] = "expert"
                    print("\033[2J\033[3J\033[H", end="") # By Claude
                    return True
                elif answer == "n":
                    return False
                else:
                    print("잘못된 입력입니다.")
                    continue
        else:
            print("잘못된 입력입니다.")
            continue

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

def show_keypad(buttons, state, is_main=False):
    console.print(f"\n 📁 현재 위치: [bold cyan]{state['current_dir']}[/bold cyan]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column()
    table.add_column()
    table.add_column()

    # 버튼 3개씩 묶어서 행으로 추가
    row = []
    for i, btn in enumerate(buttons):
        # 모드에 따른 출력 형식 지정
        if state["mode"] == "beginner":
            display_format = btn.label
        else: # state["mode"] == "expert":
            display_format = btn.command

        
        # 비기너 모드 중, 0 입력 시 명령어명 표시
        if state["mode"] == "beginner" and state["show_command"] and is_main:
            label = f"[{i+1}] {display_format}({btn.command})"
        else:
            label = f"[{i+1}] {display_format}"

        # 위험한 명령어: 진한 빨강 / 일반 명령어: 기본으로 지정 후 row에 추가
        if btn.dangerous:
            row.append(f"[bold red]{label}[/bold red]")
        else:
            row.append(label)

        # row의 크기가 3이 되면 테이블에 추가 후, row 비움
        if len(row) == 3:
            table.add_row(*row)
            row = []

    # 남은 버튼 처리 (버튼 수가 3의 배수가 아닐 때)
    if row:
        while len(row) < 3:
            row.append("")
        table.add_row(*row)

    console.print(table)
    # 멘트 — is_main일 때만 출력
    if is_main and state["mode"] == "beginner":
        if state["show_command"]:
            print("\n* 각 명령어의 이름을 보이지 않게 하고 싶다면 [0]을 입력하세요.")
        else:
            print("\n* 각 명령어의 이름을 알고 싶다면 [0]을 입력하세요.")
    console.print(Rule(style="grey50")) # By Claude
    # console.print("─" * 40)

ARG_PROMPTS = {
    "mkdir": "생성할 폴더명을 입력하세요",
    "touch": "생성할 파일명을 입력하세요",
}

keypad_buttons = [
    # 탐색 (Navigation)
    Button(label='파일 목록', command='ls'),
    Button(label='현재 위치', command='pwd'),
    Button(label='위치 이동', command='cd'),

    # 생성 (Create)
    Button(label='폴더 생성', command='mkdir'),
    Button(label='파일 생성', command='touch'),

    # 확인 (Inspect)
    Button(label='파일 보기', command='cat'),
    Button(label='화면 지우기', command='clear'),

    # 삭제 (Delete) [dangerous=True]
    Button(label='파일 삭제', command='rm',     dangerous=True),
    Button(label='폴더 삭제', command='rm -rf', dangerous=True)
]

# main 함수 추가 사항: while True 루프가 시작되기 전에 onboarding()을 호출하고, 
# 반환값이 False면 (N→N 선택) 프로그램을 종료
def main():
    if not onboarding():
        return

    while True:
        show_keypad(keypad_buttons, state, is_main=True)
        choice = input("번호를 입력하세요 [q: 종료]: ").strip()

        if choice == 'q':
            print("종료합니다.")
            break

        if state["mode"] == "beginner" and choice == '0':
            state["show_command"] = not state["show_command"]
            continue

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