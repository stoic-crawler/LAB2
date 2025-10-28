pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR   = 'venv'
        CI_LOGS    = 'ci_logs'
        IMAGE_NAME = 'arithmeticapi:latest'
        SUDO       = 'sudo -n'
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh '''
                            python3 -m venv ${VENV_DIR} || echo "venv already exists"
                            . ${VENV_DIR}/bin/activate
                            python -m ensurepip --upgrade || true
                            pip install --upgrade pip setuptools wheel
                            pip install --no-cache-dir -r requirements.txt
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh '''
                            mkdir -p ${CI_LOGS}
                            . ${VENV_DIR}/bin/activate
                            pytest -v test_app.py | tee ${CI_LOGS}/pytest.log
                        '''
                    }
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh '''
                            mkdir -p ${CI_LOGS}
                            . ${VENV_DIR}/bin/activate
                            bandit -r app -f json -o ${CI_LOGS}/bandit-report.json || true
                        '''
                    }
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh '''
                            mkdir -p ${CI_LOGS}
                            . ${VENV_DIR}/bin/activate
                            safety check --json > ${CI_LOGS}/safety-report.json || true
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    timeout(time: 15, unit: 'MINUTES') {
                        echo "Building Docker image"
                        sh "docker-compose build || true"
                    }
                }
            }
        }

        stage('Install Trivy via snap') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        echo "Installing Trivy via snap (requires sudo)"
                        sh '''
                            ${SUDO} snap install trivy --classic || echo "snap install failed"
                            ${SUDO} snap run trivy --version || true
                        '''
                    }
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh '''
                            mkdir -p ${CI_LOGS}
                            ${SUDO} snap run trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME} || true
                        '''
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        echo "Deploying Docker container"
                        sh "docker-compose up -d || true"
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${CI_LOGS}/*.json, ${CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished."
        }
    }
}
