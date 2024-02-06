#!/bin/bash

PROGRAM_NAME="manage"  # 程序名称
PROGRAM_PATH="../python/bin/python3 run.py manage"  # 启动命令
PORT=22501

# 检查程序状态
check_status() {
    pid=$(pgrep -f "$PROGRAM_NAME")
    if [ -n "$pid" ]; then
        echo "$PROGRAM_NAME is running with PID: $pid"
    else
        echo "$PROGRAM_NAME is not running"
    fi
}

# 启动程序
start_program() {
    check_status
    if pgrep -f "$PROGRAM_NAME" >/dev/null; then  # 如果程序已经在运行
        echo "$PROGRAM_NAME is already running"
    else
        echo "Starting $PROGRAM_NAME..."
        $PROGRAM_PATH >/dev/null 2>&1 &
        sleep 1  # 可根据需要适当增加等待时间
        check_status
        if ! pgrep -f "$PROGRAM_NAME" >/dev/null; then
            echo "Failed to start $PROGRAM_NAME"
            exit 1
        fi
    fi
}

# 关闭程序
stop_program() {
    check_status
    if pgrep -f "$PROGRAM_NAME" >/dev/null; then
        echo "Stopping $PROGRAM_NAME..."
        pkill -f "$PROGRAM_NAME"
        sleep 1  # 可根据需要适当增加等待时间
        check_status
        if pgrep -f "$PROGRAM_NAME" >/dev/null; then
            echo "Failed to stop $PROGRAM_NAME"
            exit 1
        fi
    else
        echo "$PROGRAM_NAME is not running"
    fi
}
stop() {
  # 确定要关闭的端口号
  port=$PORT

  # 检查端口号是否提供
  if [ -z "$port" ]; then
    echo "请提供要关闭的端口号"
    return 1
  fi

  # 检查端口是否被占用
  if lsof -i ":$port" >/dev/null; then
    # 获取占用指定端口的进程ID列表
    pids=$(lsof -t -i ":$port")
  
    # 循环终止进程
    for pid in $pids; do
      kill $pid
      echo "已终止进程 $pid"
    done
  
    echo "成功关闭端口 $port 上的所有进程"
  else
    echo "端口 $port 未被占用"
  fi
}

# 重启程序
restart_program() {
    stop
    sleep 1
    start_program
}

# 查询程序状态
status_program() {
    check_status
}

# 解析命令行参数
case "$1" in
    "start")
        start_program
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart_program
        ;;
    "status")
        status_program
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
