from pathlib import Path
from pydantic import BaseModel

# Objeto de retorno rico para facilitar a vida do desenvolvedor
class ResolvedSubdomainContext(BaseModel):
    subdomain_config: SubdomainConfig
    storage_account: StorageAccount
    cost_tracking: CostTracking

class ConfigManager:
    _instance = None
    _config: AppConfig = None

    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            if config_path:
                cls._instance._load_config(config_path)
            else:
                raise ValueError("O caminho do arquivo de configuração deve ser fornecido na primeira inicialização.")
        return cls._instance

    def _load_config(self, config_path: str):
        """Lê o YAML e injeta no Pydantic para validação estrita."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
            
        with open(path, "r", encoding="utf-8") as file:
            raw_yaml = yaml.safe_load(file)
            
        # Aqui a mágica acontece: O Pydantic valida tudo ou quebra a execução
        self._config = AppConfig(**raw_yaml)

    @property
    def config(self) -> AppConfig:
        return self._config

    def get_subdomain_context(self, domain_name: str, layer_name: str, subdomain_name: str) -> ResolvedSubdomainContext:
        """
        Retorna todas as informações necessárias para operar um subdomínio,
        resolvendo automaticamente a infraestrutura física (Storage Account) por trás dele.
        """
        try:
            domain = self._config.data_domains[domain_name]
            layer = domain.layers[layer_name]
            subdomain = layer.subdomains[subdomain_name]
        except KeyError as e:
            raise KeyError(f"Caminho não encontrado no YAML. Verifique domínio, camada ou subdomínio: {e}")

        # Busca a conta de storage associada
        storage = self._config.storage_accounts[subdomain.storage_ref]

        return ResolvedSubdomainContext(
            subdomain_config=subdomain,
            storage_account=storage,
            cost_tracking=domain.cost_tracking
        )