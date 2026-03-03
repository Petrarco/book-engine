# 1. Inicializa (pode ser na main do seu job)
config_mgr = ConfigManager("/caminho/para/configs/dev.yaml")

# 2. Busca o contexto completo do subdomínio RPF
ctx = config_mgr.get_subdomain_context(domain_name="dgf", layer_name="silver", subdomain_name="rpf")

# 3. Usa os dados já validados com autocomplete na IDE!
print(f"Lendo de: {ctx.subdomain_config.path}")
print(f"Gravando no schema: {ctx.subdomain_config.catalog_schema}")
print(f"Aplicar tags de custo no Databricks: {ctx.cost_tracking.cost_center}")

# 4. Usando para injetar credenciais no Spark
account_name = ctx.storage_account.account_name
secret_key = ctx.storage_account.client_id_secret_key
# -> Chamar o SecretManager(secret_key) e plugar no SparkSession...