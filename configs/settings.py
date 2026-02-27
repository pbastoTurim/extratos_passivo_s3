from configs.env import get_env_var

# DRIVER = get_env_var('SQL_DRIVER', required=True)
# SERVER = get_env_var('SQL_SERVER', required=True)
# DATABASE = get_env_var('SQL_DATABASE', required=True)
# USERNAME_DB = get_env_var('SQL_USERNAME', required=True)
# PASSWORD_DB = get_env_var('SQL_PASSWORD', required=True)

USER_S3= get_env_var('USER_S3', required=True)
PASSWORD_S3 = get_env_var('PASSWORD_S3', required=True)