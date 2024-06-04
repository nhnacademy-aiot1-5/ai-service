# 🤖 AI 서비스
<img width="1117" alt="image" src="https://github.com/nhnacademy-aiot1-5/ai-service/assets/98167706/12c79f7e-f0a5-4662-bdca-8bd58ff9c919">
<br>
<br>
지금까지의 전력량 데이터를 학습하고 추후 30일 전력 소비량을 예측하는 ai 서비스입니다.
<br>
<br>
<div>
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/prophet-3D5A96?style=for-the-badge&logo=prophet&logoColor=white">
<br>
<img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
<img src="https://img.shields.io/badge/influxdb-22ADF6?style=for-the-badge&logo=influxdb&logoColor=white">
<br>
<img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
<img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
<img src="https://img.shields.io/badge/nhncloud-2B5CDE?style=for-the-badge&logo=cloudera&logoColor=white">
</div>
<br>
<br>

## 🛠️ 개발 내용
### 👩‍💻 이은지
- 채널별 전력 사용량 일단위, 월단위 예측 서비스 구현
  - 학습 시작 전 데이터 백업 및 초기화
  - 데이터 조회 및 가공 : 채널별 kwh 조회 후 사용량 데이터로 가공
  - 모델 학습
    - 학습 모델 : prophet
    - main의 경우 cross validation을 통해 rmse 값이 제일 적은 파라미터 도출
    - kwh 값이 변화가 없는 채널의 경우 학습 없이 사용량을 0으로 저장
  - 예측 데이터 가공 및 저장
    - 1자리 수에서 반올림
- 장소별 총 전력 사용량 예측 서비스 구현
- 이상치 기준점 계산 서비스 구현
  - 데이터 조회 및 가공, 계산, 저장
- 서비스 스케줄링 : apsheduler를 이용해 0시 5분 이상치 도출, 0시 10분 예측 서비스를 자동으로 실행
- 모듈화 - google colab으로 작성한 코드를 intelliJ에 모듈별로 작성
- 패키징 및 배포 - setuptools를 사용하여 패키징한 후, 서버로 배포

### 👨‍💻 허시영
- InfluxDB에서 전력 데이터 분석
- 프로펫 라이브러리 학습
- 프로펫 하이퍼 파라미터(주말, 계절, 추세 고려) 교차 검증 메소드 추가
- 프로펫 모델 학습, 교차 검증, 전력 소비량 예상 데이터 그래프로 확인
- 스케줄링 작업
<br>
<br>

## 📄 참고 자료
![image](https://github.com/nhnacademy-aiot1-5/ai-service/assets/78470571/a5a8384a-16bb-472d-9836-a833b4ffa936)
