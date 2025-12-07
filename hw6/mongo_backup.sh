#!/bin/bash

# Конфигурация
BACKUP_DIR="/var/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
MONGO_HOST="localhost"
MONGO_PORT="27017"
MONGO_USER="admin"
MONGO_PASS=""  # Использовать .env файл или переменные окружения
DATABASES=("app_db" "logs_db")  # Список баз данных

# Создание директории для бэкапов
mkdir -p $BACKUP_DIR

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка подключения к MongoDB
check_mongo_connection() {
    if ! mongosh --host $MONGO_HOST --port $MONGO_PORT --quiet --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        log "ERROR: Невозможно подключиться к MongoDB"
        exit 1
    fi
}

# Бэкап всех баз данных
backup_all_databases() {
    log "Начало резервного копирования MongoDB"
    
    for DB in "${DATABASES[@]}"; do
        BACKUP_PATH="$BACKUP_DIR/${DB}_${DATE}"
        log "Бэкап базы данных: $DB"
        
        if [ -z "$MONGO_PASS" ]; then
            # Бэкап без аутентификации
            mongodump --host $MONGO_HOST --port $MONGO_PORT --db "$DB" --out "$BACKUP_PATH"
        else
            # Бэкап с аутентификацией
            mongodump --host $MONGO_HOST --port $MONGO_PORT \
                      -u "$MONGO_USER" -p "$MONGO_PASS" --authenticationDatabase admin \
                      --db "$DB" --out "$BACKUP_PATH"
        fi
        
        if [ $? -eq 0 ]; then
            log "Успешно создан бэкап: $BACKUP_PATH"
            
            # Архивирование
            tar -czf "${BACKUP_PATH}.tar.gz" -C "$BACKUP_DIR" "${DB}_${DATE}"
            log "Бэкап заархивирован: ${BACKUP_PATH}.tar.gz"
            
            # Удаление временной директории
            rm -rf "$BACKUP_PATH"
        else
            log "ERROR: Ошибка при создании бэкапа для $DB"
        fi
    done
}

# Очистка старых бэкапов
clean_old_backups() {
    log "Очистка бэкапов старше $RETENTION_DAYS дней"
    find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    log "Очистка завершена"
}

# Основная функция
main() {
    log "=== Запуск скрипта бэкапа MongoDB ==="
    check_mongo_connection
    backup_all_databases
    clean_old_backups
    log "=== Завершение скрипта бэкапа ==="
}

# Запуск основной функции
main 2>&1 | tee -a "$BACKUP_DIR/backup.log"
