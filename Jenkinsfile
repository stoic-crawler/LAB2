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
    }pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR   = 'venv'
        CI_LOGS    = 'ci_logs'
        IMAGE_NAME = 'arithmeticapi:latest'
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
                    pytest -v test_app.py --junitxml=${CI_LOGS}/pytest-results.xml | tee ${CI_LOGS}/pytest.log
                '''
            }
            post {
                always {
                    junit "${CI_LOGS}/pytest-results.xml"
                }
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
                    safety scan --json --output ${CI_LOGS}/safety-report.json || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image"
                sh "docker-compose build"
            }
        }

        stage('Install Trivy') {
            steps {
                script {
                    // Try multiple installation methods for better compatibility
                    sh '''
                        # Method 1: Try downloading binary directly (preferred)
                        if ! command -v trivy &> /dev/null; then
                            echo "Installing Trivy via direct download..."
                            wget https://github.com/aquasecurity/trivy/releases/download/v0.49.1/trivy_0.49.1_Linux-64bit.tar.gz
                            tar -xzf trivy_0.49.1_Linux-64bit.tar.gz
                            sudo mv trivy /usr/local/bin/ || echo "Moving to /usr/local/bin failed, using current directory"
                            chmod +x trivy
                        fi

                        # Method 2: Fallback to snap if direct download fails
                        if ! command -v trivy &> /dev/null && command -v snap &> /dev/null; then
                            echo "Falling back to snap installation..."
                            sudo snap install trivy --classic || echo "Snap installation failed"
                        fi

                        # Verify installation
                        trivy --version || ./trivy --version || echo "Trivy installation failed"
                    '''
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                sh '''
                    mkdir -p ${CI_LOGS}
                    # Try different trivy binary locations
                    if command -v trivy &> /dev/null; then
                        trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME} || true
                    elif [ -f "./trivy" ]; then
                        ./trivy image --severity CRITICAL,HIGH --format json -o ${CI_LOGS}/trivy-report.json ${IMAGE_NAME} || true
                    else
                        echo "Trivy not found, skipping vulnerability scan"
                        echo '{"error": "trivy not installed"}' > ${CI_LOGS}/trivy-report.json
                    fi
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                echo "Deploying Docker container"
                sh "docker-compose up -d"
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${CI_LOGS}/*.json, ${CI_LOGS}/*.log, ${CI_LOGS}/*.xml", allowEmptyArchive: true
            echo "Pipeline finished."
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
            // Add notification here (email, Slack, etc.)
        }
        unstable {
            echo "Pipeline marked as unstable!"
        }
    }
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
                    safety scan > ${CI_LOGS}/safety-report..txt || true
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


