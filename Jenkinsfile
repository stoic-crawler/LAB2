pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR = 'venv'
        CI_LOGS = 'ci_logs'
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
                    python3 -m venv venv || true
                    . venv/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                    pip install pytest bandit safety
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    mkdir -p ci_logs
                    . venv/bin/activate
                    pytest -v test_app.py --junitxml=ci_logs/pytest-results.xml | tee ci_logs/pytest.log
                '''
            }
            post {
                always {
                    junit 'ci_logs/pytest-results.xml'
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                sh '''
                    mkdir -p ci_logs
                    . venv/bin/activate
                    bandit -r app -f json -o ci_logs/bandit-report.json || true
                '''
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                sh '''
                    mkdir -p ci_logs
                    . venv/bin/activate
                    safety scan --json --output ci_logs/safety-report.json || true
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
                sh '''
                    # Try multiple installation methods
                    if ! command -v trivy &> /dev/null; then
                        echo "Installing Trivy via direct download..."
                        wget -q https://github.com/aquasecurity/trivy/releases/download/v0.18.3/trivy_0.18.3_Linux-64bit.tar.gz
                        tar -xzf trivy_0.18.3_Linux-64bit.tar.gz
                        sudo mv trivy /usr/local/bin/ || echo "Moving trivy failed"
                        rm trivy_0.18.3_Linux-64bit.tar.gz
                    fi
                    
                    # Fallback to snap
                    if ! command -v trivy &> /dev/null && command -v snap &> /dev/null; then
                        echo "Falling back to snap installation..."
                        sudo snap install trivy --classic || echo "Snap installation failed"
                    fi
                    
                    # Verify
                    trivy --version || echo "Trivy not available"
                '''
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                sh '''
                    mkdir -p ci_logs
                    if command -v trivy &> /dev/null; then
                        trivy image --severity CRITICAL,HIGH --format json -o ci_logs/trivy-report.json arithmeticapi:latest || true
                    else
                        echo "Trivy not found, skipping scan"
                        echo '{"error": "trivy not available"}' > ci_logs/trivy-report.json
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
            archiveArtifacts artifacts: 'ci_logs/*.json, ci_logs/*.log, ci_logs/*.xml', allowEmptyArchive: true
            echo "Pipeline finished."
        }
        success {
            echo "Pipeline completed successfully!"
        }
        failure {
            echo "Pipeline failed!"
        }
    }
}
