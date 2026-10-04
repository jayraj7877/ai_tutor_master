pipeline {
    agent any

    tools {
        // Uncomment and set if you have Python configured as a Jenkins tool
        // python 'Python3.11'
    }

    environment {
        // Name of the SonarQube Server configured in Jenkins -> Manage Jenkins -> System -> SonarQube servers
        SONAR_QUBE_SERVER = 'SonarQube'
        // Name of the SonarQube Scanner tool configured in Jenkins -> Manage Jenkins -> Tools -> SonarQube Scanner
        SONAR_SCANNER_TOOL = 'SonarScanner'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from Git...'
                checkout scm
            }
        }

        stage('Setup Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip setuptools
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests & Code Coverage') {
            steps {
                echo 'Running pytest unit & integration tests with coverage reporting...'
                sh '''
                    . .venv/bin/activate
                    pytest -v --cov=app --cov-report=xml:coverage.xml --cov-report=term --junitxml=test-results.xml
                '''
            }
        }

        stage('SonarQube Code Analysis') {
            steps {
                echo 'Executing SonarQube Scanner code quality and security scan...'
                script {
                    def scannerHome = tool name: "${SONAR_SCANNER_TOOL}"
                    withSonarQubeEnv("${SONAR_QUBE_SERVER}") {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps {
                echo 'Waiting for SonarQube Quality Gate result...'
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to Quality Gate failure: ${qg.status}"
                        } else {
                            echo "Quality Gate Passed successfully!"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Publishing Test Results & Cleaning Workspace...'
            junit allowEmptyResults: true, testResults: 'test-results.xml'
            archiveArtifacts artifacts: 'coverage.xml, test-results.xml', allowEmptyArchive: true
        }
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed! Please check console logs and test reports.'
        }
    }
}
