pipeline {
    agent any

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    triggers {
        // 每天北京时间 10:00 自动构建（UTC 02:00）
        cron('H 2 * * *')
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
        DINGTALK_WEBHOOK = credentials('dingtalk-webhook')
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
                        args = "-k '${params.PYTEST_KEYWORD}'"
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
                allure([
                    includeProperties: false,
                    jdk: '',
                    properties: [],
                    reportBuildPolicy: 'ALWAYS',
                    results: [[path: 'report/allure_results']]
                ])
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report/html/report.html', allowEmptyArchive: true
            archiveArtifacts artifacts: 'report/allure_report/**', allowEmptyArchive: true

            script {
                def status = currentBuild.currentResult
                def statusText = status == 'SUCCESS' ? '✅ 成功' : (status == 'FAILURE' ? '❌ 失败' : '⚠️ 不稳定')
                def envText = params.ENV?.toUpperCase() ?: 'MES'
                def duration = currentBuild.durationString.replace(' and counting', '')
                def buildUser = env.BUILD_USER ?: '定时触发'

                def payload = """{
    "msgtype": "markdown",
    "markdown": {
        "title": "UI自动化测试通知",
        "text": "### UI自动化测试通知\\n- **构建编号**: #${env.BUILD_NUMBER}\\n- **项目**: ${env.JOB_NAME}\\n- **环境**: ${envText}\\n- **状态**: ${statusText}\\n- **构建人**: ${buildUser}\\n- **持续时间**: ${duration}\\n- [点击查看构建详情](${env.BUILD_URL})"
    }
}"""

                writeFile file: 'dingtalk_payload.json', text: payload

                sh '''
                    curl -s -X POST \
                        "${DINGTALK_WEBHOOK}" \
                        -H "Content-Type: application/json" \
                        -d @dingtalk_payload.json
                '''
            }
        }
        failure {
            archiveArtifacts artifacts: 'screenshots/**', allowEmptyArchive: true
        }
    }
}
