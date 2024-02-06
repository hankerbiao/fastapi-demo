MAIN_SERVER = ["emss-server", "org.h2.tools.Server"]

FRONT_SERVER = ["grafana", "nginx"]

LOG_SERVER = ["apache-zookeeper", "kafkaServer", "logstash", "flink", "elasticsearch"]

MONITOR_SERVER = ["prometheus", "alertmanager", "pushgateway", "emss-metric-exporters"]

MIDDLEWARE_SERVER = ["postgres_exporter"]

SERVER_TYPE = {
    "MAIN_SERVER": MAIN_SERVER,
    "FRONT_SERVER": FRONT_SERVER,
    "LOG_SERVER": LOG_SERVER,
    "MONITOR_SERVER": MONITOR_SERVER,
    "MIDDLEWARE_SERVER": MIDDLEWARE_SERVER
}

ZH_EN = {
    "MAIN_SERVER": "主服务",
    "FRONT_SERVER": "前台服务",
    "LOG_SERVER": "日志服务",
    "MONITOR_SERVER": "监控服务",
    "MIDDLEWARE_SERVER": "中间件服务"
}

# EMSS 组件备份目录
BACKUP_PATH = "emss_backup"

IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

ENVS = """
export JAVA_HOME={0}/jdk-17.0.5
export CLASS_PATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
export PATH=$JAVA_HOME:$CLASS_PATH:$JAVA_HOME/bin:$PATH


"""
