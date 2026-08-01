"""
License Manager for Thamarat ERP Desktop
"""

import os
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

class LicenseManager:
    """
    Simple license management for desktop product
    """
    
    def __init__(self):
        self.license_file = Path.home() / ".thamarat" / "license.dat"
        self.trial_days = 30
        self._ensure_license_file()
    
    def _ensure_license_file(self):
        """Create license file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
        
        if not self.license_file.exists():
            # Create trial license
            trial_data = {
                "type": "trial",
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=self.trial_days)).isoformat(),
                "organization": None,
                "license_key": None
            }
            with open(self.license_file, 'w') as f:
                json.dump(trial_data, f)
    
    def _read_license(self):
        """Read license file"""
        try:
            with open(self.license_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _write_license(self, data):
        """Write license file"""
        with open(self.license_file, 'w') as f:
            json.dump(data, f)
    
    def is_valid(self) -> bool:
        """Check if license is valid"""
        license_data = self._read_license()
        
        if not license_data:
            return False
        
        license_type = license_data.get("type", "trial")
        
        if license_type == "trial":
            expires_at = datetime.fromisoformat(license_data.get("expires_at"))
            return datetime.now() < expires_at
        
        elif license_type == "full":
            expires_at = license_data.get("expires_at")
            if expires_at:
                return datetime.now() < datetime.fromisoformat(expires_at)
            return True
        
        return False
    
    def get_license_info(self) -> dict:
        """Get license information"""
        license_data = self._read_license()
        
        if not license_data:
            return {"valid": False, "type": "none"}
        
        info = {
            "valid": self.is_valid(),
            "type": license_data.get("type", "trial"),
            "organization": license_data.get("organization"),
            "created_at": license_data.get("created_at")
        }
        
        if info["type"] == "trial":
            expires_at = datetime.fromisoformat(license_data.get("expires_at"))
            days_remaining = (expires_at - datetime.now()).days
            info["expires_at"] = license_data.get("expires_at")
            info["days_remaining"] = max(0, days_remaining)
        else:
            info["expires_at"] = license_data.get("expires_at")
        
        return info
    
    def activate_license(self, license_key: str, organization: str) -> bool:
        """Activate full license with license key"""
        # Simple license validation (in production, this would verify against a server)
        if len(license_key) < 20:
            return False
        
        # Create permanent license
        license_data = {
            "type": "full",
            "organization": organization,
            "license_key": license_key,
            "created_at": datetime.now().isoformat(),
            "expires_at": None  # Perpetual license
        }
        
        self._write_license(license_data)
        return True
    
    def get_machine_id(self) -> str:
        """Get unique machine identifier"""
        import socket
        hostname = socket.gethostname()
        return hashlib.sha256(hostname.encode()).hexdigest()[:16]
