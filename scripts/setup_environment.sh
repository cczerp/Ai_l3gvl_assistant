#!/bin/bash
# ========================================
# LEGAL-AI ASSISTANT - AUTOMATED SETUP SCRIPT
# ========================================
# This script automates the setup of your development environment
# Run with: bash scripts/setup_environment.sh
# Last updated: 2025-12-10

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ========================================
# STEP 1: Check Prerequisites
# ========================================
print_step "Step 1: Checking prerequisites..."

# Check Python version
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python ${PYTHON_VERSION} found"

# Check pip
if ! command_exists pip3; then
    print_error "pip3 is not installed. Installing pip..."
    python3 -m ensurepip --upgrade
fi
print_success "pip3 found"

# Check git
if ! command_exists git; then
    print_warning "Git is not installed. Some features may not work."
else
    print_success "Git found"
fi

# ========================================
# STEP 2: Create Virtual Environment
# ========================================
print_step "Step 2: Creating Python virtual environment..."

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate || {
    print_error "Failed to activate virtual environment"
    exit 1
}
print_success "Virtual environment activated"

# ========================================
# STEP 3: Upgrade pip and Install Build Tools
# ========================================
print_step "Step 3: Upgrading pip and installing build tools..."

pip install --upgrade pip setuptools wheel
print_success "Build tools updated"

# ========================================
# STEP 4: Install Dependencies
# ========================================
print_step "Step 4: Installing Python dependencies from requirements.txt..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# ========================================
# STEP 5: Install Optional Dependencies
# ========================================
print_step "Step 5: Installing optional dependencies..."

# Check for GPU (NVIDIA CUDA)
if command_exists nvidia-smi; then
    print_success "NVIDIA GPU detected! Installing CUDA-enabled PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pip uninstall -y faiss-cpu
    pip install faiss-gpu
    print_success "GPU-accelerated PyTorch and FAISS installed"
else
    print_warning "No NVIDIA GPU detected. Using CPU-only versions."
fi

# Install spaCy language model
print_step "Installing spaCy English model..."
python -m spacy download en_core_web_sm
print_success "spaCy model installed"

# Install Playwright (for web scraping)
if command_exists playwright; then
    print_step "Installing Playwright browsers..."
    playwright install
    print_success "Playwright browsers installed"
else
    print_warning "Playwright not found. Skipping browser installation."
fi

# ========================================
# STEP 6: Create Directory Structure
# ========================================
print_step "Step 6: Creating directory structure..."

mkdir -p data/state_laws
mkdir -p data/federal_laws
mkdir -p data/cases
mkdir -p data/legal_dictionaries
mkdir -p data/vector_store
mkdir -p data/embeddings
mkdir -p data/cache
mkdir -p models
mkdir -p logs
mkdir -p config
mkdir -p scripts
mkdir -p tests

print_success "Directory structure created"

# ========================================
# STEP 7: Setup Environment Variables
# ========================================
print_step "Step 7: Setting up environment variables..."

if [ -f ".env" ]; then
    print_warning ".env file already exists. Skipping creation."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
        print_warning "⚠️  IMPORTANT: Edit .env and fill in your API keys!"
    else
        print_error ".env.example not found! Cannot create .env"
    fi
fi

# ========================================
# STEP 8: Verify Database Connection (Supabase)
# ========================================
print_step "Step 8: Verifying database configuration..."

if [ -f ".env" ]; then
    if grep -q "SUPABASE_URL=" .env && grep -q "SUPABASE_KEY=" .env; then
        SUPABASE_URL=$(grep "SUPABASE_URL=" .env | cut -d '=' -f2)
        if [ -n "$SUPABASE_URL" ] && [ "$SUPABASE_URL" != "" ]; then
            print_success "Supabase configuration found in .env"
            print_warning "Remember to run the schema: scripts/supabase_schema.sql"
        else
            print_warning "Supabase URL is empty. Please configure it in .env"
        fi
    else
        print_warning "Supabase configuration not found in .env"
    fi
fi

# ========================================
# STEP 9: Download Model Information
# ========================================
print_step "Step 9: Checking for local AI models..."

LLAMA3_PATH="models/llama3-8b-instruct"
MIXTRAL_PATH="models/mixtral-8x7b-instruct"

if [ -d "$LLAMA3_PATH" ]; then
    print_success "Llama3 model found at $LLAMA3_PATH"
else
    print_warning "Llama3 model not found."
    echo "   To download:"
    echo "   1. Install HuggingFace CLI: pip install huggingface-hub"
    echo "   2. Login: huggingface-cli login"
    echo "   3. Download: huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --local-dir $LLAMA3_PATH"
fi

if [ -d "$MIXTRAL_PATH" ]; then
    print_success "Mixtral model found at $MIXTRAL_PATH"
else
    print_warning "Mixtral model not found."
    echo "   To download:"
    echo "   1. Install HuggingFace CLI: pip install huggingface-hub"
    echo "   2. Login: huggingface-cli login"
    echo "   3. Download: huggingface-cli download mistralai/Mixtral-8x7B-Instruct-v0.1 --local-dir $MIXTRAL_PATH"
fi

# ========================================
# STEP 10: Test Installation
# ========================================
print_step "Step 10: Testing installation..."

python3 -c "
import fastapi
import torch
import transformers
import sentence_transformers
import supabase
print('✓ All core packages imported successfully!')
"

if [ $? -eq 0 ]; then
    print_success "Installation test passed!"
else
    print_error "Installation test failed. Some packages may not be installed correctly."
fi

# ========================================
# STEP 11: Display Next Steps
# ========================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. ${BLUE}Configure API Keys:${NC}"
echo "   Edit .env and add your API keys:"
echo "   - OPENAI_API_KEY (or use free alternatives)"
echo "   - HUGGINGFACE_API_KEY (free tier available)"
echo "   - GROQ_API_KEY (free tier available)"
echo "   - SUPABASE_URL and SUPABASE_KEY"
echo ""
echo "2. ${BLUE}Setup Database:${NC}"
echo "   Run the schema in Supabase SQL Editor:"
echo "   cat scripts/supabase_schema.sql | pbcopy  # Copy to clipboard (Mac)"
echo "   Or paste scripts/supabase_schema.sql into Supabase dashboard"
echo ""
echo "3. ${BLUE}Download AI Models (Optional):${NC}"
echo "   For local inference:"
echo "   bash scripts/download_models.sh"
echo ""
echo "4. ${BLUE}Scrape Legal Data:${NC}"
echo "   python scripts/scrape_to_supabase.py"
echo ""
echo "5. ${BLUE}Start the API Server:${NC}"
echo "   source venv/bin/activate"
echo "   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "6. ${BLUE}Run Tests:${NC}"
echo "   pytest tests/"
echo ""
echo -e "${YELLOW}DOCUMENTATION:${NC}"
echo "   Setup guide: docs/SETUP_GUIDE.md"
echo "   Free AI options: docs/FREE_AI_OPTIONS.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
echo ""
