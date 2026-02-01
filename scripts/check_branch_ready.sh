#!/bin/bash
# Check if employee-conversation-service branch is ready to merge to main

echo "======================================================================"
echo "Branch Readiness Check for Merging to Main"
echo "======================================================================"

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "\n📍 Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" != *"employee"* ]]; then
    echo "⚠️  Warning: You're not on an employee service branch"
fi

# Check for uncommitted changes
echo -e "\n🔍 Checking for uncommitted changes..."
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ You have uncommitted changes:"
    git status --short
    echo -e "\n💡 Commit these before merging:"
    echo "   git add ."
    echo "   git commit -m 'your message'"
else
    echo "✅ No uncommitted changes"
fi

# Check what files changed in this branch compared to main
echo -e "\n📊 Files changed compared to main:"
git fetch origin main 2>/dev/null
CHANGED_FILES=$(git diff --name-only origin/main...HEAD)

if [[ -z "$CHANGED_FILES" ]]; then
    echo "⚠️  No changes detected"
else
    # Count changes by service
    EMPLOYEE_CHANGES=$(echo "$CHANGED_FILES" | grep "employee_conversation_service" | wc -l)
    CLIENT_CHANGES=$(echo "$CHANGED_FILES" | grep "client_need_service" | wc -l)
    OTHER_CHANGES=$(echo "$CHANGED_FILES" | grep -v "employee_conversation_service" | grep -v "client_need_service" | wc -l)

    echo "   Employee service files: $EMPLOYEE_CHANGES"
    echo "   Client service files: $CLIENT_CHANGES"
    echo "   Other files: $OTHER_CHANGES"

    if [[ $CLIENT_CHANGES -gt 0 ]]; then
        echo -e "\n⚠️  WARNING: You modified client_need_service files:"
        echo "$CHANGED_FILES" | grep "client_need_service"
        echo -e "\n💡 This may cause conflicts when merging to main."
        echo "   Consider reverting these changes or discuss with team."
    fi

    echo -e "\n📋 All changed files:"
    echo "$CHANGED_FILES"
fi

# Check if tests pass
echo -e "\n🧪 Checking if employee service is runnable..."
if [[ -f "backend/employee_conversation_service/main.py" ]]; then
    echo "✅ Employee service main.py exists"
else
    echo "❌ Employee service main.py not found"
fi

if [[ -f "backend/employee_conversation_service/.env" ]]; then
    echo "✅ Employee service .env exists"
else
    echo "⚠️  Employee service .env not found (will need configuration)"
fi

# Check recent commits
echo -e "\n📝 Recent commits on this branch:"
git log --oneline -5

# Summary
echo -e "\n======================================================================"
echo "Summary"
echo "======================================================================"

if [[ -z $(git status --porcelain) ]] && [[ $EMPLOYEE_CHANGES -gt 0 ]] && [[ $CLIENT_CHANGES -eq 0 ]]; then
    echo "✅ Branch is ready to merge to main!"
    echo -e "\n📋 To merge:"
    echo "   git checkout main"
    echo "   git merge $CURRENT_BRANCH"
    echo "   git push origin main"
elif [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  Commit your changes first"
elif [[ $CLIENT_CHANGES -gt 0 ]]; then
    echo "⚠️  Review client_need_service changes before merging"
else
    echo "✅ Branch looks good, but verify changes are complete"
fi

echo "======================================================================"
