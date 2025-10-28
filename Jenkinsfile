pipeline {
    agent any

    options {
        skipStagesAfterUnstable()
        timestamps()
    }

    environment {
        VENV_DIR   = 'venv'
        CI_LOGS    = 'ci_logs'
        IMAGE_NAME = 'lab-2-app'
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
                    timeout(time: 12, unit: 'MINUTES') {
                        sh '''
                            echo "=== Debug: user / python info ==="
                            id
                            which python3 || true
                            python3 --version || true
                            echo "PWD: $(pwd)"
                        '''
                        sh """
                            echo "=== Create venv if missing ==="
                            /usr/bin/python3 -m venv "${env.VENV_DIR}" || { echo "venv creation failed or already exists"; }
                            echo "=== venv contents after creation ==="
                            ls -la "${env.VENV_DIR}" || true
                        """
                        sh """
                            echo "=== Ensure pip inside venv (if supported) ==="
                            if [ -x "${env.VENV_DIR}/bin/python" ]; then
                                "${env.VENV_DIR}/bin/python" -m ensurepip --upgrade 2>/dev/null || echo "ensurepip not available or failed"
                                "${env.VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel || echo "pip upgrade failed (will try to proceed)"
                                echo "=== venv/bin contents ==="
                                ls -la "${env.VENV_DIR}/bin" || true
                            else
                                echo "ERROR: ${env.VENV_DIR}/bin/python not found"
                                exit 2
                            fi
                        """
                        sh """
                            echo "=== Installing requirements via venv python -m pip ==="
                            "${env.VENV_DIR}/bin/python" -m pip install --no-cache-dir -r requirements.txt || true
                        """
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            // capture pytest exit code but do not abort the pipeline
                            sh "${env.VENV_DIR}/bin/python -m pytest -v test_app.py | tee ${env.CI_LOGS}/pytest.log"
                        }
                    }
                }
            }
        }

        stage('Static Code Analysis (Bandit)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "${env.VENV_DIR}/bin/python -m bandit -r app -f json -o ${env.CI_LOGS}/bandit-report.json" 
                        }
                    }
                }
            }
        }

        stage('Dependency Vulnerabilities (Safety)') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "${env.VENV_DIR}/bin/python -m safety check --json > ${env.CI_LOGS}/safety-report.json" 
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    timeout(time: 20, unit: 'MINUTES') {
                        echo "Building Docker image"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "docker-compose build"
                        }
                    }
                }
            }
        }

        stage('Install Trivy') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        echo "Installing Trivy with apt"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh '''
                                set -e
                                apt-get update
                                apt-get install -y trivy || true
                                trivy --version || true
                            '''
                        }
                    }
                }
            }
        }

        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        sh "mkdir -p ${env.CI_LOGS}"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "trivy image --severity CRITICAL,HIGH --format json -o ${env.CI_LOGS}/trivy-report.json ${env.IMAGE_NAME}:latest || true"
                        }
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    timeout(time: 10, unit: 'MINUTES') {
                        echo "Deploying Docker container"
                        catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                            sh "docker-compose up -d || true"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Archiving CI logs..."
            archiveArtifacts artifacts: "${env.CI_LOGS}/*.json, ${env.CI_LOGS}/*.log", allowEmptyArchive: true
            echo "Pipeline finished."
        }
    }
}
