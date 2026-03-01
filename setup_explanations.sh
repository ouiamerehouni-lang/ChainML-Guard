#!/bin/bash
# ChainML Guard - Explanation Feature - Quick Deploy Script
# Run this script to set up and test the explanation feature

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║              ChainML Guard - Explanation Feature Setup                  ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if in correct directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: Must be run from ChainML-Guard project root${NC}"
    echo "Current directory: $(pwd)"
    echo "Expected: /home/mahmoud/Desktop/ChainML-Guard"
    exit 1
fi

echo -e "${GREEN}✓${NC} Correct directory confirmed"
echo ""

# Step 1: Check prerequisites
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Checking Prerequisites"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check dataset
if [ -f "data/dataset_final.csv" ]; then
    echo -e "${GREEN}✓${NC} Dataset found: data/dataset_final.csv"
else
    echo -e "${RED}✗${NC} Dataset NOT found: data/dataset_final.csv"
    echo "  Please ensure the dataset exists before continuing."
    exit 1
fi

# Check model files
if [ -f "models/fraud_model.h5" ] && [ -f "models/scaler.pkl" ]; then
    echo -e "${GREEN}✓${NC} Model files found: fraud_model.h5, scaler.pkl"
else
    echo -e "${RED}✗${NC} Model files NOT found in models/"
    echo "  Please train the model first using: python train_model.py"
    exit 1
fi

# Check new files exist
echo ""
echo "Checking implementation files..."
if [ -f "scripts/compute_thresholds.py" ]; then
    echo -e "${GREEN}✓${NC} scripts/compute_thresholds.py"
else
    echo -e "${RED}✗${NC} scripts/compute_thresholds.py NOT found"
    exit 1
fi

if [ -f "utils/explanations.py" ]; then
    echo -e "${GREEN}✓${NC} utils/explanations.py"
else
    echo -e "${RED}✗${NC} utils/explanations.py NOT found"
    exit 1
fi

if [ -f "utils/__init__.py" ]; then
    echo -e "${GREEN}✓${NC} utils/__init__.py"
else
    echo -e "${RED}✗${NC} utils/__init__.py NOT found"
    exit 1
fi

echo ""

# Step 2: Compute thresholds
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Computing Thresholds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "thresholds.json" ]; then
    echo -e "${YELLOW}⚠${NC} thresholds.json already exists"
    read -p "Do you want to recompute? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Recomputing thresholds..."
        python scripts/compute_thresholds.py
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓${NC} Thresholds computed successfully"
        else
            echo -e "${RED}✗${NC} Failed to compute thresholds"
            exit 1
        fi
    else
        echo -e "${GREEN}✓${NC} Using existing thresholds.json"
    fi
else
    echo "Computing thresholds for the first time..."
    python scripts/compute_thresholds.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Thresholds computed successfully"
    else
        echo -e "${RED}✗${NC} Failed to compute thresholds"
        exit 1
    fi
fi

echo ""

# Step 3: Verify thresholds
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Verifying Thresholds"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "thresholds.json" ]; then
    echo "Thresholds file content:"
    cat thresholds.json | python -m json.tool
    echo ""
    echo -e "${GREEN}✓${NC} Thresholds file is valid JSON"
else
    echo -e "${RED}✗${NC} thresholds.json not found"
    exit 1
fi

echo ""

# Step 4: Optional test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Optional Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Run test script to verify explanations? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python test_explanation_feature.py
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓${NC} Test completed successfully"
    else
        echo -e "${YELLOW}⚠${NC} Test had some issues (check output above)"
    fi
fi

echo ""

# Final summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✓${NC} All prerequisites verified"
echo -e "${GREEN}✓${NC} Thresholds computed and saved"
echo -e "${GREEN}✓${NC} Ready to run Flask app"
echo ""
echo "Next steps:"
echo "  1. Start the Flask app:"
echo "     ${YELLOW}python app.py${NC}"
echo ""
echo "  2. Open browser:"
echo "     ${YELLOW}http://localhost:5000${NC}"
echo ""
echo "  3. Analyze an address to see the explanation feature!"
echo ""
echo "Documentation:"
echo "  - Quick Start:        QUICK_REFERENCE.txt"
echo "  - Full Guide:         EXPLANATION_FEATURE.md"
echo "  - Implementation:     IMPLEMENTATION_SUMMARY.md"
echo "  - Architecture:       ARCHITECTURE_DIAGRAM.md"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                        Ready to deploy! 🚀                               ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
