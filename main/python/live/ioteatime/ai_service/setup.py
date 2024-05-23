from setuptools import setup, find_packages

setup(
    name='ai_service',
    version='1.0',
    description='시간별 이상치를 계산하고, 30일 예상 전력 사용량을 계산하는 ai service 입니다.',
    author='eunji',
    packages=find_packages(),
    install_requires=[
        'redis',
        'pymysql',
        'sqlalchemy',
        'influxdb_client',
        'apscheduler'
    ]
)