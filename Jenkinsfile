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
                sh '''
                    python3 -m venv ${VENV_DIR} || true
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    # install dev/test tools
                    pip install pytest bandit safety
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    mkdir -p ${CI_LOGS}
                    . ${VENV_DIR}/bin/activate
                    pytest -v test_app.py | tee ${CI_LOGS}/pytest.log
                '''
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                sh '''
                    mkdir -p ${CI_LOGS}
                    . ${VENV_DIR}/bin/activate
                    bandit -r app -f json -o ${CI_LOGS}/bandit-report.json || true
                '''
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                sh '''
                    mkdir -p ${CI_LOGS}
                    . ${VENV_DIR}/bin/activate
                    safety check --json > ${CI_LOGS}/safety-report.json || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image"
                sh "docker-compose build || true"
            }
        }

        stage('Install Trivy via snap') {
            steps {
                echo "Installing Trivy via snap (requires sudo)"
                sh '''
                    ${SUDO} snap install trivy --classic || echo "snap install failed"
                    ${SUDO} snap run trivy --version || true
                '''
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                sh '''
                    mkdir -p ${CI_LOGS}
                    ${SUDO} snap run trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME} || true
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying Docker container"
                sh "docker-compose up -d || true"
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
