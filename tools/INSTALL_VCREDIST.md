# Visual C++ Redistributable 설치 가이드

## 문제
PyTorch 사용 시 DLL 로딩 에러 발생:
```
OSError: [WinError 1114] DLL 초기화 루틴을 실행할 수 없습니다.
```

## 해결 방법

### 1. Visual C++ Redistributable 설치

**다운로드:**
- https://aka.ms/vs/17/release/vc_redist.x64.exe

**설치 방법:**
1. 위 링크 클릭 또는 브라우저에 복사
2. vc_redist.x64.exe 다운로드
3. 다운로드한 파일 실행
4. 설치 마법사 따라 진행
5. 컴퓨터 재시작 (권장)

### 2. 설치 후 확인

PowerShell에서 실행:
```powershell
cd d:\03.Code\LightRAG
.\tools\start_all.ps1
```

### 3. 추가 문제 발생 시

다른 버전도 설치:
- Visual C++ 2015-2022: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Visual C++ 2013: https://aka.ms/highdpimfc2013x64enu
- Visual C++ 2012: https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe

## 대안: 임베딩 서버 없이 실행

LightRAG 설정에서 OpenAI API 임베딩 사용:
```python
# config.yaml 또는 환경변수에서
embedding_func: openai
```
