# app/src/automation/api_clients/account_mapper.py - SIMPLIFIED IMPORT

# Import the modular AccountMapper from the new structure
from .account_mapper.core import AccountMapper
from .account_mapper.config import ACCOUNT_MAPPING, PLATFORM_MAPPING

# Maintain backward compatibility
__all__ = ['AccountMapper', 'ACCOUNT_MAPPING', 'PLATFORM_MAPPING']

# This file now just imports from the modular structure
# All the actual logic is in account_mapper/ subfolder