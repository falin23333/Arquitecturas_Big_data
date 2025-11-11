import os
user="postgres.zgqbxstkrpfqlpvwiiip"
password="DNDefault123"
host="aws-1-eu-central-2.pooler.supabase.com"
port="5432"
dbname="postgres"


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))