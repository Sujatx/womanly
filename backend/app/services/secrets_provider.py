"""
Pluggable secrets management provider.
Supports multiple backends: environment variables, AWS Secrets Manager, HashiCorp Vault, Azure KeyVault.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timedelta
import os
import json
import logging

logger = logging.getLogger(__name__)


class SecretProvider(ABC):
    """Abstract base class for secret providers."""
    
    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        """Retrieve a secret by name."""
        pass
    
    @abstractmethod
    def get_secret_json(self, secret_name: str) -> dict:
        """Retrieve a secret as JSON."""
        pass
    
    @abstractmethod
    def secret_exists(self, secret_name: str) -> bool:
        """Check if a secret exists."""
        pass


class EnvSecretProvider(SecretProvider):
    """Secrets provider using environment variables."""
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from environment variable."""
        value = os.getenv(secret_name)
        if not value:
            raise ValueError(f"Secret '{secret_name}' not found in environment variables")
        return value
    
    def get_secret_json(self, secret_name: str) -> dict:
        """Retrieve JSON secret from environment variable."""
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if secret exists in environment variables."""
        return secret_name in os.environ


class AWSSecretsManagerProvider(SecretProvider):
    """Secrets provider using AWS Secrets Manager."""
    
    def __init__(self, region_name: str = "us-east-1"):
        try:
            import boto3
            self.client = boto3.client("secretsmanager", region_name=region_name)
        except ImportError:
            raise ImportError("boto3 is required for AWS Secrets Manager. Install with: pip install boto3")
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if "SecretString" in response:
                return response["SecretString"]
            else:
                # Binary secret
                logger.error(f"Binary secrets not supported: {secret_name}")
                raise ValueError(f"Secret '{secret_name}' is binary")
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from AWS: {str(e)}")
            raise
    
    def get_secret_json(self, secret_name: str) -> dict:
        """Retrieve JSON secret from AWS Secrets Manager."""
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if secret exists in AWS Secrets Manager."""
        try:
            self.client.describe_secret(SecretId=secret_name)
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False


class HashiCorpVaultProvider(SecretProvider):
    """Secrets provider using HashiCorp Vault."""
    
    def __init__(self, vault_url: str, vault_token: str, mount_path: str = "secret"):
        try:
            import hvac
            self.client = hvac.Client(url=vault_url, token=vault_token)
            self.mount_path = mount_path
        except ImportError:
            raise ImportError("hvac is required for HashiCorp Vault. Install with: pip install hvac")
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Vault."""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
            data = response["data"]["data"]
            
            # If single key-value, return the value; otherwise return first value
            if len(data) == 1:
                return list(data.values())[0]
            elif "value" in data:
                return data["value"]
            else:
                raise ValueError(f"Secret '{secret_name}' does not contain a 'value' field")
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from Vault: {str(e)}")
            raise
    
    def get_secret_json(self, secret_name: str) -> dict:
        """Retrieve JSON secret from Vault."""
        response = self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
        return response["data"]["data"]
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if secret exists in Vault."""
        try:
            self.client.secrets.kv.v2.read_secret_version(path=secret_name, mount_point=self.mount_path)
            return True
        except self.client.exceptions.InvalidPath:
            return False


class AzureKeyVaultProvider(SecretProvider):
    """Secrets provider using Azure Key Vault."""
    
    def __init__(self, vault_url: str, credential=None):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            
            if credential is None:
                credential = DefaultAzureCredential()
            
            self.client = SecretClient(vault_url=vault_url, credential=credential)
        except ImportError:
            raise ImportError(
                "Azure SDK is required for Azure Key Vault. "
                "Install with: pip install azure-identity azure-keyvault-secrets"
            )
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from Azure Key Vault."""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{secret_name}' from Azure Key Vault: {str(e)}")
            raise
    
    def get_secret_json(self, secret_name: str) -> dict:
        """Retrieve JSON secret from Azure Key Vault."""
        value = self.get_secret(secret_name)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"Secret '{secret_name}' is not valid JSON")
    
    def secret_exists(self, secret_name: str) -> bool:
        """Check if secret exists in Azure Key Vault."""
        try:
            self.client.get_secret(secret_name)
            return True
        except Exception:
            return False


class SecretRotationTracker:
    """Tracks secret rotation history."""
    
    def __init__(self):
        self.rotation_log: dict = {}
    
    def record_rotation(self, secret_name: str, rotated_by: str = "system"):
        """Record that a secret was rotated."""
        self.rotation_log[secret_name] = {
            "rotated_at": datetime.utcnow().isoformat(),
            "rotated_by": rotated_by,
        }
        logger.info(f"Secret '{secret_name}' rotated by {rotated_by}")
    
    def get_rotation_status(self, secret_name: str, rotation_interval_days: int = 90) -> dict:
        """Get rotation status for a secret."""
        if secret_name not in self.rotation_log:
            return {"rotated": False, "needs_rotation": True}
        
        last_rotation = datetime.fromisoformat(self.rotation_log[secret_name]["rotated_at"])
        days_since_rotation = (datetime.utcnow() - last_rotation).days
        needs_rotation = days_since_rotation >= rotation_interval_days
        
        return {
            "rotated": True,
            "last_rotated_at": self.rotation_log[secret_name]["rotated_at"],
            "days_since_rotation": days_since_rotation,
            "needs_rotation": needs_rotation,
        }


# Global rotation tracker
rotation_tracker = SecretRotationTracker()


def get_secret_provider(provider_type: str = "env", **kwargs) -> SecretProvider:
    """Factory function to create a secret provider."""
    providers = {
        "env": EnvSecretProvider,
        "aws": AWSSecretsManagerProvider,
        "vault": HashiCorpVaultProvider,
        "azure": AzureKeyVaultProvider,
    }
    
    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return providers[provider_type](**kwargs)
