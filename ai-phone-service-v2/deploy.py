""""
Deployment script for the AI Phone Answering Service.
"""
import os
import sys
import logging
import argparse
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    # Check if required packages are installed
    required_packages = [
        "fastapi", "uvicorn", "twilio", "google-cloud-speech", "google-cloud-texttospeech",
        "google-api-python-client", "google-auth-oauthlib",
        "msal", "caldav", "requests", "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            logger.info("All dependencies installed successfully")
        except subprocess.CalledProcessError:
            logger.error("Failed to install dependencies")
            return False
    
    logger.info("All dependencies are satisfied")
    return True

def build_frontend():
    """Build the frontend application."""
    logger.info("Building frontend application...")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    
    if not os.path.exists(frontend_dir):
        logger.error(f"Frontend directory not found: {frontend_dir}")
        return False
    
    try:
        # Install frontend dependencies
        subprocess.check_call(["npm", "install"], cwd=frontend_dir)
        
        # Build the frontend
        subprocess.check_call(["npm", "run", "build"], cwd=frontend_dir)
        
        logger.info("Frontend built successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build frontend: {str(e)}")
        return False

def run_tests():
    """Run the test suite."""
    logger.info("Running tests...")
    
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")
    
    if not os.path.exists(tests_dir):
        logger.error(f"Tests directory not found: {tests_dir}")
        return False
    
    try:
        # Run unit tests
        unit_test_path = os.path.join(tests_dir, "test_ai_phone_service.py")
        logger.info("Running unit tests...")
        subprocess.check_call([sys.executable, unit_test_path])
        
        # Run integration tests
        integration_test_path = os.path.join(tests_dir, "integration_test.py")
        logger.info("Running integration tests...")
        subprocess.check_call([sys.executable, integration_test_path])
        
        logger.info("All tests passed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed: {str(e)}")
        return False

def start_services():
    """Start all services."""
    logger.info("Starting services...")
    
    # Start the main application
    main_script = os.path.join(os.path.dirname(__file__), "main.py")
    
    if not os.path.exists(main_script):
        logger.error(f"Main script not found: {main_script}")
        return False
    
    try:
        # Start the application
        logger.info("Starting main application...")
        subprocess.Popen([sys.executable, main_script])
        
        # Wait for the application to start
        logger.info("Waiting for services to start...")
        time.sleep(5)
        
        # Check if the application is running
        try:
            response = requests.get("http://localhost:8000/")
            if response.status_code == 200:
                logger.info("Services started successfully")
                return True
            else:
                logger.error(f"Service health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to the service")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start services: {str(e)}")
        return False

def deploy():
    """Deploy the AI Phone Answering Service."""
    logger.info("Deploying AI Phone Answering Service...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        return False
    
    # Build frontend
    if not build_frontend():
        logger.error("Frontend build failed")
        return False
    
    # Run tests
    if not run_tests():
        logger.error("Tests failed")
        return False
    
    # Start services
    if not start_services():
        logger.error("Failed to start services")
        return False
    
    logger.info("AI Phone Answering Service deployed successfully!")
    logger.info("The service is now running at http://localhost:8000/")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the AI Phone Answering Service")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip building frontend")
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)
    
    # Build frontend if not skipped
    if not args.skip_frontend:
        if not build_frontend():
            logger.error("Frontend build failed")
            sys.exit(1)
    
    # Run tests if not skipped
    if not args.skip_tests:
        if not run_tests():
            logger.error("Tests failed")
            sys.exit(1)
    
    # Start services
    if not start_services():
        logger.error("Failed to start services")
        sys.exit(1)
    
    logger.info("AI Phone Answering Service deployed successfully!")
    logger.info("The service is now running at http://localhost:8000/")
