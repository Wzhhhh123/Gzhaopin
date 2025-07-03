import pymysql
from pymysql.cursors import DictCursor

# 主备配置
DB_CONFIGS = [
    {
        "name": "内网",
        "host": "192.168.1.185",
        "user": "root",
        "password": "Wzh010310",
        "database": "zhaopin",
        "charset": "utf8mb4"
    },
    {
        "name": "外网",
        "host": "jq777.cn",
        "user": "root",
        "password": "Wzh010310",
        "database": "zhaopin",
        "charset": "utf8mb4"
    }
]

# ✅ 用于缓存选中的配置
_selected_config = None

def init_db_config():
    """程序启动时运行一次，决定使用哪个配置"""
    global _selected_config
    for config in DB_CONFIGS:
        try:
            config_clean = {k: v for k, v in config.items() if k != 'name'}
            # 只做连接测试，不用返回连接对象
            conn = pymysql.connect(**config_clean, connect_timeout=2)
            conn.close()
            _selected_config = config_clean
            print(f"✅ 已选择 {config['name']} 数据库：{config['host']}")
            return
        except Exception as e:
            print(f"⚠️ 无法连接 {config['name']}（{config['host']}），错误：{e}")
    raise Exception("❌ 所有数据库配置均无法连接")

def connect_db():
    """后续统一调用这个函数获取连接"""
    if not _selected_config:
        raise Exception("未初始化数据库配置，请先调用 init_db_config()")
    return pymysql.connect(**_selected_config, cursorclass=DictCursor)
