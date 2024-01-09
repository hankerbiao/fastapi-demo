COMPOSE_LIST = ["grafana", "logstash", "flink"]

MAIN_SERVER = ["server-1.0.0-RELEASE.jar", "org.h2.tools.Server"]

FRONT_SERVER = ["grafana", "nginx"]

LOG_SERVER = ["apache-zookeeper", "kafka", "logstash", "flink", "elasticsearch"]

MONITOR_SERVER = ["prometheus", "alertmanager", "pushgateway"]

SERVER_TYPE = {
    "MAIN_SERVER": MAIN_SERVER,
    "FRONT_SERVER": FRONT_SERVER,
    "LOG_SERVER": LOG_SERVER,
    "MONITOR_SERVER": MONITOR_SERVER
}

# EMSS 组件备份目录
BACKUP_PATH = "backup"

IP_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

ENVS = """
export JAVA_HOME={0}/jdk-17.0.5
export CLASS_PATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
export PATH=$JAVA_HOME:$CLASS_PATH:$JAVA_HOME/bin:$PATH
"""