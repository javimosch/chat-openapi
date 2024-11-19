# Optional Systems Documentation

This document outlines various systems that can be integrated into applications when specified. These systems are designed to be modular, configurable, and disabled by default unless explicitly required.

## Implementation Triggers and Guidelines

### When to Implement a System

Consider implementing a system when:
1. The application reaches a specific complexity threshold
2. A clear pattern of repetitive tasks emerges
3. Multiple parts of the application need similar functionality
4. Technical debt would be prevented by early implementation

### System Implementation Checklist
- [ ] Is this system really needed at this stage?
- [ ] Will it solve more problems than it creates?
- [ ] Can we start with a simpler solution?
- [ ] Is the overhead worth the benefits?

### Proposing New Systems

When identifying a new pattern or need in the application, consider proposing a new system if:
1. The functionality would be used in multiple places
2. It solves a common development challenge
3. It can be implemented simply (< 300 lines total)
4. It can be toggled on/off easily

### System Proposal Template
```markdown
## [System Name]

### Problem Statement
- What problem does this solve?
- Why is it needed?

### Core Features
- List minimal viable features
- Focus on essentials

### Configuration
- ENV variables
- Default values
- Toggle mechanisms

### Implementation Estimate
- Approximate lines of code
- Integration complexity
- Maintenance overhead
```

## Logging System

### Core Features
- Default stdout logging
- Configurable verbosity levels
- Optional file/DB output
- Disable/Enable via ENV
- Function-level logging

### Configuration
```env
LOG_ENABLED=true
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_OUTPUT=stdout  # stdout, file, db
LOG_FILE_PATH=/var/log/app.log  # If file output
LOG_FORMAT=json  # json, text
LOG_MAX_SIZE=10MB  # Max file size before rotation
```

### Implementation Example
```python
# utils/logger.py
import logging
import sys
import json
from typing import Union, Dict

class AppLogger:
    """
    Flexible logging system that can output to stdout, file, or database
    Supports different verbosity levels and can be entirely disabled
    """
    def __init__(self, config: Dict):
        self.enabled = config.get('LOG_ENABLED', False)
        if not self.enabled:
            return

        self.logger = logging.getLogger('app')
        self.level = getattr(logging, config.get('LOG_LEVEL', 'INFO'))
        self.logger.setLevel(self.level)
        
        # Configure handler based on output type
        handler = self._get_handler(config)
        formatter = self._get_formatter(config)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _get_handler(self, config: Dict) -> logging.Handler:
        output = config.get('LOG_OUTPUT', 'stdout')
        if output == 'file':
            return logging.FileHandler(config.get('LOG_FILE_PATH'))
        return logging.StreamHandler(sys.stdout)

    def _get_formatter(self, config: Dict) -> logging.Formatter:
        if config.get('LOG_FORMAT') == 'json':
            return logging.Formatter(
                '{"time":"%(asctime)s", "level":"%(levelname)s", "message":%(message)s}'
            )
        return logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def log(self, level: str, message: Union[str, Dict], **kwargs):
        if not self.enabled:
            return
            
        if isinstance(message, dict):
            message = json.dumps(message)
        
        getattr(self.logger, level.lower())(message, **kwargs)
```

## Events System

### Core Features
- Business action tracking
- File system storage by default
- Automatic file pruning (> 1MB)
- Optional DB storage
- Structured event format
- Disable/Enable via ENV

### Configuration
```env
EVENTS_ENABLED=true
EVENTS_STORAGE=fs  # fs, db
EVENTS_PATH=/var/events
EVENTS_MAX_FILE_SIZE=1MB
EVENTS_RETENTION_DAYS=30
```

### Implementation Example
```python
# utils/events.py
from datetime import datetime
from pathlib import Path
import json
from typing import Dict

class EventSystem:
    """
    Business event tracking system with file system or database storage
    Automatically prunes old events and manages storage size
    """
    def __init__(self, config: Dict):
        self.enabled = config.get('EVENTS_ENABLED', False)
        if not self.enabled:
            return
            
        self.storage = config.get('EVENTS_STORAGE', 'fs')
        self.events_path = Path(config.get('EVENTS_PATH', '/var/events'))
        self.max_size = 1_000_000  # 1MB in bytes
        
        if self.storage == 'fs':
            self.events_path.mkdir(parents=True, exist_ok=True)

    async def record(self, event_type: str, data: Dict):
        if not self.enabled:
            return

        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': data
        }

        if self.storage == 'fs':
            await self._store_fs(event)
        else:
            await self._store_db(event)

    async def _store_fs(self, event: Dict):
        current_file = self.events_path / f"events_{datetime.utcnow():%Y%m%d}.json"
        
        # Check file size and rotate if needed
        if current_file.exists() and current_file.stat().st_size > self.max_size:
            self._rotate_files()

        with current_file.open('a') as f:
            json.dump(event, f)
            f.write('\n')

    async def _store_db(self, event: Dict):
        # Implement DB storage when specified
        pass

    def _rotate_files(self):
        # Implement file rotation logic
        pass
```

## Authentication and User System

### Core Features
- Session/JWT based authentication
- Email/password authentication
- User status management
- Multi-role support
- Flexible role hierarchy
- Database storage

### Configuration
```env
AUTH_ENABLED=true
AUTH_METHOD=jwt  # jwt, session
AUTH_JWT_SECRET=your-secret
AUTH_JWT_EXPIRE=24h
AUTH_SESSION_EXPIRE=24h
```

### Implementation Example
```python
# models/user.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    email: EmailStr
    password_hash: str
    roles: List[str] = ['user']
    is_active: bool = True
    last_login: Optional[datetime] = None

# services/auth.py
from datetime import datetime, timedelta
import jwt
from typing import Optional, Dict

class AuthService:
    """
    Flexible authentication system supporting both JWT and session-based auth
    Includes role-based access control and user management
    """
    def __init__(self, config: Dict):
        self.method = config.get('AUTH_METHOD', 'jwt')
        self.secret = config.get('AUTH_JWT_SECRET')
        self.expire_hours = int(config.get('AUTH_JWT_EXPIRE', '24'))

    async def authenticate(self, email: str, password: str) -> Optional[str]:
        user = await self._verify_credentials(email, password)
        if not user or not user.is_active:
            return None

        if self.method == 'jwt':
            return self._create_jwt(user)
        return self._create_session(user)

    def _create_jwt(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(hours=self.expire_hours)
        return jwt.encode(
            {
                'sub': user.email,
                'roles': user.roles,
                'exp': expire
            },
            self.secret
        )

    async def has_role(self, user: User, required_roles: List[str]) -> bool:
        return any(role in user.roles for role in required_roles)
```

## CLI System

### Core Features
- No authentication by default
- CRUD operations support
- JSON input/output
- Single action commands
- Database management
- System control

### Configuration
```env
CLI_ENABLED=true
CLI_AUTH_REQUIRED=false
CLI_DEFAULT_FORMAT=json
```

### Implementation Example
```python
# cli/main.py
import click
import json
from typing import Dict

@click.group()
@click.option('--format', default='json', type=click.Choice(['json', 'text']))
@click.pass_context
def cli(ctx, format):
    """Command line interface for application management"""
    ctx.ensure_object(dict)
    ctx.obj['format'] = format

@cli.command()
@click.argument('input_file', type=click.File('r'))
@click.pass_context
def create_user(ctx, input_file):
    """Create a new user from JSON input"""
    try:
        data = json.load(input_file)
        # Implement user creation logic
        if ctx.obj['format'] == 'json':
            click.echo(json.dumps({'status': 'success', 'user': data}))
        else:
            click.echo(f"Created user: {data['email']}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--level', default='INFO')
def set_log_level(level):
    """Change the application log level"""
    # Implement log level change
    click.echo(f"Log level set to {level}")

if __name__ == '__main__':
    cli(obj={})
```

### Example Usage
```bash
# Create user from JSON file
$ ./cli.py create-user user.json

# Change log level
$ ./cli.py set-log-level --level DEBUG

# Get system status
$ ./cli.py status --format json
```

## Integration Guidelines

1. **System Independence**
   - Each system should be independently toggleable
   - Systems should not have hard dependencies on each other
   - Use interface abstractions for cross-system communication

2. **Configuration Priority**
   ```
   ENV vars > Config files > Default values
   ```

3. **Performance Considerations**
   - Log rotation for file-based systems
   - Database indexing for auth/user system
   - Batch operations in CLI
   - Asynchronous event recording

4. **Security Practices**
   - Sanitize all logged data
   - Encrypt sensitive information
   - Rate limit authentication attempts
   - Validate CLI inputs

5. **Extensibility**
   - Use abstract base classes
   - Implement plugin systems
   - Allow custom formatters
   - Support middleware
