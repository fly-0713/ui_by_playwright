pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(
            name: 'ENV',
            choices: ['mes', 'h5'],
            description: '运行环境'
        )
        string(
            name: 'PYTEST_KEYWORD',
            defaultValue: '',
            description: 'pytest -k 关键字过滤（为空运行全部）'
        )
    }

    environment {
        ENV = "${params.ENV ?: 'mes'}"
        MES_USERNAME = credentials('mes-ui-test-username')
        MES_PASSWORD = credentials('mes-ui-test-password')
        H5_USERNAME = credentials('mes-ui-test-h5-username')
        H5_PASSWORD = credentials('mes-ui-test-h5-password')
        PYTHONUNBUFFERED = '1'
        ALLURE_CMD = 'allure'
    }

    stages {
        stage('检出代码') {
            steps {
                checkout scm
            }
        }

        stage('安装依赖') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip
                    pip install -r requirements-ci.txt
                '''
            }
        }

        stage('安装 Playwright 浏览器及依赖') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m playwright install chromium
                '''
            }
        }

        stage('执行 UI 测试') {
            steps {
                script {
                    def args = ""
                    if (params.PYTEST_KEYWORD?.trim()) {
                        args = "-k ${params.PYTEST_KEYWORD}"
                    }
                    sh """
                        . venv/bin/activate
                        python ci_run.py ${args}
                    """
                }
            }
        }

        stage('生成 Allure 报告') {
            steps {
                sh '''
                    if command -v allure >/dev/null 2>&1; then
                        allure generate report/allure_results -o report/allure_report --clean
                    else
                        echo "[警告] allure 命令未找到，跳过 Allure 报告生成"
                    fi
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report/html/report.html', allowEmptyArchive: true
            archiveArtifacts artifacts: 'report/allure_report/**', allowEmptyArchive: true
        }
        failure {
            archiveArtifacts artifacts: 'screenshots/**', allowEmptyArchive: true
        }
    }
}
