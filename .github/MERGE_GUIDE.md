# Merge Guide: Employee Service to Main

## Branch Structure

- `main` - Contains client_need_service
- `feature/jo-employee-conversation-service` - Contains employee_conversation_service development

## Merge Strategy

### Safe Merge (Recommended)

```bash
# 1. Ensure your employee branch is clean
git checkout feature/jo-employee-conversation-service
git status

# 2. Update from main (optional, to avoid conflicts)
git fetch origin main
git merge origin/main
# Resolve any conflicts in employee_conversation_service only

# 3. Switch to main and merge
git checkout main
git merge feature/jo-employee-conversation-service

# 4. Verify only employee service changed
git diff HEAD~1 --stat
# Should show only employee_conversation_service files

# 5. Push to main
git push origin main
```

### What Gets Merged

Only files you **modified** on the employee branch:
- ✅ `backend/employee_conversation_service/**` (your changes)
- ✅ `backend/test_employee_conversation.py` (new file)
- ❌ `backend/client_need_service/**` (unchanged, stays as-is in main)

### Rollback if Needed

```bash
# If merge goes wrong
git reset --hard HEAD~1

# Or create a backup first
git branch backup-main
git merge feature/jo-employee-conversation-service
```

## File Organization

### Main Branch
```
backend/
├── client_need_service/          # Client needs extraction
│   ├── api/
│   ├── services/
│   ├── models/
│   └── main.py (port 8000)
│
└── employee_conversation_service/ # Employee skills extraction (merged from feature branch)
    ├── api/
    ├── services/
    ├── models/
    └── main.py (port 8001)
```

### Both Services Are Independent
- Different databases
- Different ports
- Different .env files
- Can run simultaneously
- Can be deployed separately

## Testing After Merge

```bash
# Start both services
cd backend

# Terminal 1: Client service
uvicorn client_need_service.main:app --port 8000

# Terminal 2: Employee service
uvicorn employee_conversation_service.main:app --port 8001

# Test both
curl http://localhost:8000/api/v1/health
curl http://localhost:8001/api/v1/health
```

## Future Development

### Working on Employee Service Again

```bash
# Option 1: Continue on same branch
git checkout feature/jo-employee-conversation-service
# Make changes
git add backend/employee_conversation_service/
git commit -m "feat: new employee feature"
git push

# Merge to main again when ready
git checkout main
git merge feature/jo-employee-conversation-service

# Option 2: New feature branch
git checkout -b feature/employee-service-enhancement
# Make changes, merge to main when done
```

### Working on Client Service

```bash
git checkout -b feature/client-service-enhancement
# Work only in client_need_service/
git commit -m "feat: new client feature"
git checkout main
git merge feature/client-service-enhancement
```

## Common Issues

### Issue: Merge conflicts in client_need_service
**Solution**: You probably shouldn't have changed those files. Keep main's version:
```bash
git checkout --theirs backend/client_need_service/path/to/file
```

### Issue: Want to update both services
**Solution**: Create separate branches or work on main directly:
```bash
# Work on main for changes affecting both
git checkout main
# Make changes
git commit -m "feat: update both services"
```

## Best Practices

1. ✅ **One service per branch** - Easier to review and merge
2. ✅ **Separate .env files** - Each service has its own config
3. ✅ **Independent databases** - No shared tables
4. ✅ **Different ports** - Can run both at once
5. ✅ **Clear commit messages** - Prefix with service name

## Questions?

- Employee service port: 8001
- Client service port: 8000
- Both use same Azure credentials (can share)
- Both use PostgreSQL (different databases)
