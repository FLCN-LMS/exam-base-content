#!/bin/bash
# Generate RSA key pair for exam data encryption

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PRIVATE_KEY="$REPO_ROOT/encryption.key"
PUBLIC_KEY="$REPO_ROOT/encryption.pub"

# Check if keys already exist
if [ -f "$PRIVATE_KEY" ] || [ -f "$PUBLIC_KEY" ]; then
    echo -e "${YELLOW}⚠️  Key files already exist!${NC}"
    echo "   Private key: $PRIVATE_KEY"
    echo "   Public key: $PUBLIC_KEY"
    read -p "Do you want to regenerate? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo -e "${GREEN}Generating RSA key pair...${NC}"

# Generate private key
openssl genrsa -out "$PRIVATE_KEY" 2048

# Extract public key
openssl rsa -in "$PRIVATE_KEY" -pubout -out "$PUBLIC_KEY"

echo -e "${GREEN}✓ Key pair generated successfully!${NC}"
echo ""
echo "Files created:"
echo "  • Private key: $PRIVATE_KEY (DO NOT COMMIT!)"
echo "  • Public key:  $PUBLIC_KEY (commit this)"
echo ""
echo "Next steps:"
echo "  1. Commit the public key:"
echo "     git add $PUBLIC_KEY"
echo "     git commit -m 'chore: add RSA public key for encryption'"
echo "     git push"
echo ""
echo "  2. Secure the private key:"
echo "     - Store it in a secure location"
echo "     - Never commit it to the repository"
echo "     - Only share with authorized team members"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Back up your private key safely!${NC}"
