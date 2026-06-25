# Terminal Tutor - terminal_tutor.py

# By Claude: For Exploring Directory
import os

# By Claude: For Executing Terminal Command
import subprocess 

# By Claude: For Rendering Terminal UI
from rich.console import Console
from rich.table import Table
from rich.rule import Rule # By Claude: Variable-length separator in UI

console = Console()

state = {
    "mode": "",                 # 현재 모드 (온보딩 후 "beginner" 또는 "normal"로 설정됨)
    "show_command": False,      # 명령어명 토글 상태
    "current_dir": os.getcwd()  # 현재 경로
}

class Button:
    def __init__(self, label, command, dangerous=False):
        self.label = label # label: 버튼에 표시될 이름 (예: "ls")
        self.command = command # command: 실행할 터미널 명령어 (예: "ls") 
        self.dangerous = dangerous # dangerous: 위험한 명령어 여부 (True면 경고 표시)

    def execute(self, state):
        # 1. subprocess로 self.command를 실행 
        result = subprocess.run(
            self.command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=state["current_dir"]
        )

        # 2. 실행 결과 반환 (출력 없으면 에러 메시지 반환)
        return result.stdout or result.stderr

def onboarding():
    while True:
        # 1. 사용자에게 y/n 입력을 받음
        answer = input("터미널을 처음 사용해 보시나요? [y/n]: ").strip()

        # 2. y면 항상 True, n->y이면 True, n->n이면 False를 반환
        if answer == "y":
            state["mode"] = "beginner"
            input(f"터미널 세상에 오신 걸 환영합니다!\n"
                  f"Terminal Tutor는 사용자님이 터미널 환경에 익숙해질 수 있도록 도움을 주는 프로그램입니다.\n"
                  f"본 프로그램에서 제공되는 터미널 명령어들을 통해 터미널에 익숙해지세요.\n"
                  f"그리고 터미널에 익숙해 졌다면 저에게 말씀해 주세요! [Enter]\n")
            # By Claude: macOS에서 clear는 스크롤 버퍼를 지우지 않음. ANSI 이스케이프 코드로 직접 처리.
            print("\033[2J\033[3J\033[H", end="")
            return True
        elif answer == "n":
            while True:
                answer = input(f"Terminal Tutor는 터미널 환경이 낯선 분들을 위해 설계된 프로그램입니다.\n"
                               f"터미널이 이미 익숙하시다면 기존 터미널 환경이 더 편하실 수도 있습니다.\n"
                               f"그래도 한번 둘러보시겠습니까? [y/n]\n").strip()
                if answer == "y":
                    state["mode"] = "normal"
                    # By Claude: macOS에서 clear는 스크롤 버퍼를 지우지 않음. ANSI 이스케이프 코드로 직접 처리.
                    print("\033[2J\033[3J\033[H", end="")
                    return True
                elif answer == "n":
                    console.print("\nTerminal Tutor가 필요 없으시다면 아래 명령어로 직접 삭제하실 수 있습니다:\n")
                    console.print("[bold red]rm -rf Terminal-Tutor/[/bold red]", justify="center")
                    console.print("\n오늘 하루 좋은 터미널 생활되세요!\n")
                    return False
                else:
                    print("잘못된 입력입니다.")
                    continue
        else:
            print("잘못된 입력입니다.")
            continue

def warn_user():
    # 1. 위험 경고 메시지를 출력
    print(f"⚠️  위험한 명령어입니다!")

    # 2. 서브 루프 시작 (y/n 입력 단계)
    while True:
        # 사용자에게 y/n 입력을 받음
        answer = input("실행하시겠습니까? [y/n]: ").strip()

        # y면 True, n이면 False를 반환
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else:
            print("잘못된 입력입니다.")
            continue

# Terminal-Tutor 폴더 및 내부 파일 삭제 방지용 블랙리스트
PROTECTED_FILES = {"terminal_tutor.py", "README.md", ".gitignore"} # rm 대상에서 제외할 파일
PROTECTED_DIRS = {"venv", ".git", "Terminal-Tutor"} # rm -r 대상에서 제외할 폴더

def get_arg_buttons(command, state):
    # 현재 디렉토리 안에 있는 모든 파일·폴더 이름을 리스트로 가져옴(숨김 파일도 포함)
    entries = os.listdir(state["current_dir"])

    if command == "cd":
        folders = [e for e in entries if os.path.isdir(os.path.join(state["current_dir"], e))] # By Claude: List Comprehension
        dot_entries = ["..", "."]
        targets = dot_entries + sorted(folders)
    elif command == "rm -r":
        targets = sorted([e for e in entries 
                          if os.path.isdir(os.path.join(state["current_dir"], e))
                          and e not in PROTECTED_DIRS]) # 삭제 방지용 블랙리스트에 포함된 폴더 필터링
    elif command == "rm":
        targets = sorted([e for e in entries 
                          if os.path.isfile(os.path.join(state["current_dir"], e))
                          and e not in PROTECTED_FILES]) # 삭제 방지용 블랙리스트에 포함된 파일 필터링
    elif command == "cat":
        targets = sorted([e for e in entries 
                          if os.path.isfile(os.path.join(state["current_dir"], e))])
    else:
        targets = sorted(entries)

    # "cd .."와 같은 인자를 포함한 명령어 객체들을 생성 후 반환
    button_list = []
    for t in targets:
        if t in ["..", "."]:
            if t == "..":
                dot_label = ".." if state["mode"] == "normal" else "..(상위 폴더로 이동)"
            else:
                dot_label = "." if state["mode"] == "normal" else ".(현재 폴더)"
            button_list.append(Button(label=dot_label, command=f"{command} {t}"))
        else:
            button_list.append(Button(label=t, command=f"{command} {t}"))
    return button_list

def show_keypad(buttons, state, is_main=False):
    if is_main:
        console.print(f" 📁 현재 위치: [bold cyan]{state['current_dir']}[/bold cyan]\n")

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column()
    table.add_column()
    table.add_column()

    # 버튼 3개씩 묶어서 행으로 추가
    row = []
    for i, btn in enumerate(buttons):
        # 모드에 따른 출력 형식 지정
        if state["mode"] == "normal" and is_main:
            display_format = btn.command
        else:
            display_format = btn.label
        
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
            table.add_row(*row) # By Claude: List Unpacking
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
        print("* 터미널에 익숙해지셨다면 [g]를 입력하세요.")
    console.print(Rule(style="grey50"))

def graduation():
    # By Claude: macOS에서 clear는 스크롤 버퍼를 지우지 않음. ANSI 이스케이프 코드로 직접 처리.
    print("\033[2J\033[3J\033[H", end="")
    console.print("터미널에 익숙해지셨군요!")
    console.print("더 이상 Terminal Tutor가 필요 없으시다면, 아래 명령어로 직접 삭제하실 수 있습니다:\n")
    console.print("[bold red]rm -rf Terminal-Tutor/[/bold red]", justify="center")
    input("\n앞으로의 터미널 생활에 행운이 있기를 바랍니다! [Enter]\n")

def run_simple(btn, state):
    # run_with_input(), run_with_selection()과 인터페이스를 통일하기 위한 래퍼
    return btn.execute(state)

# By Claude: mkdir, touch 실행 시 사용자에게 표시할 입력 안내 문구
ARG_PROMPTS = {
    "mkdir": "생성할 폴더명을 입력하세요",
    "touch": "생성할 파일명을 입력하세요"
}

def run_with_input(btn, state):
    # 1. ARG_PROMPTS에서 안내 문구 가져오기
    prompt = ARG_PROMPTS[btn.command]
    
    # 2. 서브 루프 시작 (인자 입력 단계)
    while True:
        # 입력 받기
        arg = input(f"{prompt} [b: 뒤로]: ").strip()

        # 'b': None 반환 (메인 루프 복귀 신호)
        if arg == 'b': 
            return None
        
        # 빈 입력: 멘트 출력 후 재입력 (서브 루프)
        elif not arg:
            print("디렉터리 또는 파일명을 입력해주세요.")
            continue

        # 정상 입력: 명령어 실행 후 결과 반환
        else:
            # 이미 존재하는 이름인지 확인
            target_path = os.path.join(state["current_dir"], arg)
            if os.path.exists(target_path):
                if btn.command == "mkdir":
                    print(f"'{arg}' 폴더가 이미 존재합니다.")
                elif btn.command == "touch":
                    print(f"'{arg}' 파일이 이미 존재합니다.")
                continue
            
            temp_btn = Button(btn.label, f"{btn.command} {arg}", btn.dangerous)

            # mkdir, touch의 경우 성공해도 stdout이 비어 있어 temp_btn.execute(state)의 리턴값이 ""임
            temp_btn.execute(state)
            
            # 리턴값을 버리는 대신 성공 메시지 생성
            if btn.command == "mkdir":
                return f"✅ '{arg}' 폴더가 생성되었습니다."
            elif btn.command == "touch":
                return f"✅ '{arg}' 파일이 생성되었습니다."

SELECTION_PROMPTS = {
    "cd":    "이동할 폴더의 번호를 입력하세요",
    "cat":   "확인할 파일의 번호를 입력하세요",
    "rm":    "삭제할 파일의 번호를 입력하세요",
    "rm -r": "삭제할 폴더의 번호를 입력하세요"
}

def run_with_selection(btn, state):
    # 1. get_arg_buttons() 호출
    arg_buttons = get_arg_buttons(btn.command, state)

    if not arg_buttons: # 빈 리스트: 멘트 출력 후 None 반환
        print("선택 가능한 항목이 없습니다.")
        return None
    
    # 2. 서브 루프 시작 (인자 입력 단계)
    while True:
        print()

        # show_keypad() 출력
        show_keypad(arg_buttons, state)
        
        # 입력 받기
        prompt = SELECTION_PROMPTS.get(btn.command, "번호를 입력하세요") # 키 없으면 기본 문구로 반환
        arg_choice = input(f"{prompt} [b: 뒤로]: ").strip()
        
        # 'b': None 반환
        if arg_choice == 'b':
            return None

        # 숫자 아님 / 범위 초과: 멘트 출력 후 서브 루프 재수행
        if not arg_choice.isdigit():
            print("[*] 안의 숫자와 문자만 입력하세요")
            continue
        arg_index = int(arg_choice) - 1
        if not (0 <= arg_index < len(arg_buttons)):
            print("[*] 안의 숫자와 문자만 입력하세요")
            continue
    
        # 정상 선택: 명령어 실행 후 결과 반환
        selected = arg_buttons[arg_index]
        if btn.command == "cd":
            try:
                os.chdir(selected.command.replace(f"{btn.command} ", ""))
                state["current_dir"] = os.getcwd()
                result = f"✅ {state['current_dir']} 로 이동했습니다."
            except PermissionError:
                result = f"❌ '{selected.label}' 폴더에 접근 권한이 없습니다."
            return result
        else:
            result = selected.execute(state)
            if btn.command in ["rm", "rm -r"]: # rm, rm -r 성공 메시지 생성
                result = f"✅ '{selected.label}' 을(를) 삭제했습니다."
            return result

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
    Button(label='폴더 삭제', command='rm -r',  dangerous=True)
]

def main():
    # 1. 온보딩 실행, False 반환 시 종료
    if not onboarding():
        return

    # 2. 메인 루프 시작
    while True:
        console.print(Rule(style="grey50"))

        # 3. 키패드 출력
        show_keypad(keypad_buttons, state, is_main=True)

        # 4. 입력 받기
        choice = input("번호를 입력하세요 [q: 종료]: ").strip()
        
        # ----- case1: 프로그램 내장 기능 -----
        # 5. [q]: 종료 멘트 출력 후 메인 루프 탈출
        if choice == 'q':
            if state["mode"] == "normal":
                # By Claude: macOS에서 clear는 스크롤 버퍼를 지우지 않음. ANSI 이스케이프 코드로 직접 처리.
                print("\033[2J\033[3J\033[H", end="")
                console.print("잘 둘러보셨나요? Terminal Tutor가 필요 없으시다면 아래 명령어로 직접 삭제하실 수 있습니다:\n")
                console.print("[bold red]rm -rf Terminal-Tutor/[/bold red]", justify="center")
                input(f"\n오늘 하루 좋은 터미널 생활되세요! [Enter]\n")
            else:
                print("종료합니다.")
            break
        
        # 6. [g]: graduation() 호출 후 메인 루프 탈출 (beginner 모드일 때만)
        if state["mode"] == "beginner" and choice == 'g':
            graduation()
            break
        
        # 7. [0]: 명령어명 토글 후 메인 루프 재수행 (beginner 모드일 때만)
        if state["mode"] == "beginner" and choice == '0':
            state["show_command"] = not state["show_command"]
            # By Claude: macOS에서 clear는 스크롤 버퍼를 지우지 않음. ANSI 이스케이프 코드로 직접 처리.
            print("\033[2J\033[3J\033[H", end="")
            continue
        
        # ----- case2: 잘못된 입력 -----
        # 8. 유효하지 않은 입력: 멘트 출력 후 메인 루프 재수행 (isdigit() 체크 + 범위 체크 한 번에)
        if not choice.isdigit():
            print("[*] 안의 숫자와 문자만 입력하세요")
            continue

        index = int(choice) - 1
        if not (0 <= index < len(keypad_buttons)):
            print("[*] 안의 숫자와 문자만 입력하세요")
            continue

        # ----- case3: 명령어 실행 -----
        # 9. btn = keypad_buttons[index]
        btn = keypad_buttons[index]
        
        # 10. btn.dangerous이면 warn_user() 호출
        if btn.dangerous:
            if not warn_user(): # n: 메인 루프 재수행
                continue
            # y: if 블록 통과 후, 계속 진행
        
        # 11. btn의 종류에 따라 분기
        #     - case3-1 (ls, pwd, clear): run_simple() 호출
        #     - case3-2 (mkdir, touch):   run_with_input() 호출
        #     - case3-3 (cd, cat, rm, rm -r): run_with_selection() 호출
        if btn.command in ["ls", "pwd", "clear"]:
            result = run_simple(btn, state)
        elif btn.command in ["mkdir", "touch"]:
            result = run_with_input(btn, state)
        elif btn.command in ["cd", "cat", "rm", "rm -r"]:
            result = run_with_selection(btn, state)
        
        # 12. 결과 출력
        if result is None: # case3-2나 case3-3에서 b를 눌러 None이 반환되는 경우
            pass
        elif btn.command == "cat" and result == "": # cat 결과가 빈 파일인 경우
            print("빈 파일입니다.")
        else:
            print(result)

if __name__ == "__main__":
    main()