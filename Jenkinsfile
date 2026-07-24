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

        stage('清理历史报告') {
            steps {
                sh '''
                    rm -rf report/allure_results/* report/allure_report/* report/html/* report/junit.xml screenshots/* dingtalk_payload.json datas/shared_data.json
                    mkdir -p report/allure_results report/allure_report report/html screenshots
                '''
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
                        python ci_run.py ${args} \
                            --ignore=testcases/test_app_test_nopass.py \
                            --ignore=testcases/test_app_handle_abnormality.py \
                            --ignore=testcases/test_app_repair_over.py \
                            --ignore=testcases/test_app_review_abnormality.py
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

            junit testResults: 'report/junit.xml', allowEmptyResults: true

            allure includeProperties: false, jdk: '', results: [[path: 'report/allure_results']]

            script {
                def status = currentBuild.currentResult
                def statusText = status == 'SUCCESS' ? '✅ 成功' : (status == 'FAILURE' ? '❌ 失败' : '⚠️ 不稳定')
                def envText = params.ENV?.toUpperCase() ?: 'MES'
                def duration = currentBuild.durationString.replace(' and counting', '')
                def buildUser = env.BUILD_USER ?: '定时触发'

                def junitFile = 'report/junit.xml'
                def total = 0
                def passed = 0
                def failed = 0
                def skipped = 0

                if (fileExists(junitFile)) {
                    def content = readFile(junitFile)
                    def testsMatcher = content =~ /tests="(\d+)"/
                    def failuresMatcher = content =~ /failures="(\d+)"/
                    def errorsMatcher = content =~ /errors="(\d+)"/
                    def skippedMatcher = content =~ /skipped="(\d+)"/

                    total = testsMatcher ? testsMatcher[0][1].toInteger() : 0
                    failed = (failuresMatcher ? failuresMatcher[0][1].toInteger() : 0) + (errorsMatcher ? errorsMatcher[0][1].toInteger() : 0)
                    skipped = skippedMatcher ? skippedMatcher[0][1].toInteger() : 0
                    passed = total - failed - skipped
                }

                def payload = """{
    "msgtype": "markdown",
    "markdown": {
        "title": "UI自动化测试通知",
        "text": "### UI自动化测试通知\\n- **构建编号**: #${env.BUILD_NUMBER}\\n- **项目**: ${env.JOB_NAME}\\n- **环境**: ${envText}\\n- **状态**: ${statusText}\\n- **执行**: ${total} 条（成功 ${passed}，失败 ${failed}，跳过 ${skipped}）\\n- **构建人**: ${buildUser}\\n- **持续时间**: ${duration}\\n- [点击查看构建详情](${env.BUILD_URL})"
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
