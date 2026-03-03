from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, model_validator
import yaml

# ==========================================
# 1. Modelos de Infraestrutura e Custos
# ==========================================
class StorageAccount(BaseModel):
    account_name: str
    auth_type: str
    tenant_id: str
    client_id_secret_key: str

class CostTracking(BaseModel):
    cost_center: str
    owner: str
    project: Optional[str] = "core-library" # Valor default caso não seja preenchido

# ==========================================
# 2. Modelos de Domínio e Subdomínio (Data Mesh)
# ==========================================
class SubdomainConfig(BaseModel):
    storage_ref: str
    container: str
    path: str
    catalog_schema: str

class LayerConfig(BaseModel):
    subdomains: Dict[str, SubdomainConfig]

class DataDomain(BaseModel):
    cost_tracking: CostTracking
    layers: Dict[str, LayerConfig]

# ==========================================
# 3. Modelo Raiz (Agregador)
# ==========================================
class AppConfig(BaseModel):
    environment: str
    storage_accounts: Dict[str, StorageAccount]
    data_domains: Dict[str, DataDomain]
    
    # Placeholders para as outras sessões do YAML
    databases: Optional[Dict[str, Any]] = None
    spark_config: Optional[Dict[str, Any]] = None
    email: Optional[Dict[str, Any]] = None

    # Validação Avançada: Garante integridade referencial do YAML
    @model_validator(mode='after')
    def check_storage_references(self):
        for domain_name, domain in self.data_domains.items():
            for layer_name, layer in domain.layers.items():
                for sub_name, sub in layer.subdomains.items():
                    if sub.storage_ref not in self.storage_accounts:
                        raise ValueError(
                            f"Erro de Integridade no YAML: A referência de storage '{sub.storage_ref}' "
                            f"usada no subdomínio '{sub_name}' (Camada: {layer_name}, Domínio: {domain_name}) "
                            f"não existe no bloco 'storage_accounts'."
                        )
        return self