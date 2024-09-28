import soundfile as sf
import subprocess


def speech_to_text(*, original_file_path: str, ):   # 음성 인식
    # TODO 경로 .env에 쓰고 세팅에 설정 후 가져오기 + 경로 변경

    # 1. 파일 경로 설정
    flac_file_path = "audio.mp3"  # (test 음성) 음성인식 하고자 하는 음성경로로 ********************변경***********************

    # 2. 기본 경로 설정
    base_dir = "/data/jwbaek/guum1/espnet/egs2/2test/asr1/"  # 현재 이 코드가 실행되는 경로 ******************변경**********************

    # 3. Bash 스크립트를 실행하기 위한 인수 설정
    bash_script_path = f"{base_dir}evaluate_asr_whisper.sh"  # 실행할 bash 스크립트 경로
    outdir = f"{base_dir}output"  # 결과 파일을 저장할 디렉토리
    whisper_tag = "medium"
    whisper_dir = f"{base_dir}exp/whisper"
    decode_options = '{"task": "transcribe", "language": "ko"}'
    waveform_data = flac_file_path

    # Bash 명령어와 인수를 포함한 리스트
    command = [
        bash_script_path,
        "--whisper_tag", whisper_tag,
        "--whisper_dir", whisper_dir,
        "--decode_options", decode_options,
        waveform_data,  # npy 파일 경로를 전달
        outdir
    ]
    # 스크립트를 실행할 디렉토리 설정
    working_directory = base_dir

    # 4. subprocess.run을 사용하여 스크립트 실행
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=working_directory)
        print("Script output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error during script execution:", e.stderr)

    ''' 결과 출력 '''
    # 파일 경로 설정
    file_path = f"{base_dir}output/text"

    # 파일 열기 및 읽기
    with open(file_path, 'r', encoding='utf-8') as file:
        # 파일의 전체 내용을 읽음
        content = file.read()

    # TODO 파일 삭제

    # 읽은 내용 출력
    print(content.split('  ')[1])