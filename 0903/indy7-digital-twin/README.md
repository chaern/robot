# Indy7 Digital Twin

Neuromeka Indy7 픽앤플레이스 및 2×2×2 팔레타이징 흐름을 확인하는 브라우저 기반 오프라인 시뮬레이터입니다.

## 실행

저장소의 `python` 폴더에서 실행합니다.

```powershell
uv --cache-dir .uv-cache run python -m http.server 8080 --directory ..\web\indy7-digital-twin
```

브라우저에서 <http://localhost:8080>을 엽니다.

## 기능

- Indy7 6축 로봇 절차형 3D 시각화
- 마우스 드래그 카메라 회전 및 휠 확대/축소
- Pick/Drop TCP 좌표와 100 mm 접근·회수 경로
- 2×2×2 팔레타이징 애니메이션
- DO.0/DO.1 그리퍼 상태 표시
- 실행, 일시정지, 한 단계 실행, 초기화 및 속도 조절

현재 버전은 안전한 오프라인 시뮬레이션 전용입니다. 실제 Indy7에 명령을 전송하지 않습니다.
