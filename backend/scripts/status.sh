#!/bin/bash
# Status script for ai-safety-eval-dash Backend

set -e

echo "📊 ai-safety-eval-dash Backend Status"
echo "=============================================="

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local path=${3:-"/health"}
    local protocol=${4:-"http"}

    echo -n "🔍 $service_name: "

    if curl -f -s "${protocol}://localhost:${port}${path}" > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy or not running"
    fi
}

# Function to check Docker container status
check_container() {
    local container_name=$1
    local display_name=${2:-$container_name}

    echo -n "🐳 $display_name: "

    if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
        status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "not found")
        if [ "$status" = "running" ]; then
            echo "✅ Running"
        else
            echo "⚠️  $status"
        fi
    else
        echo "❌ Not running"
    fi
}

echo ""
echo "🐳 Docker Containers:"
echo "--------------------"

# Check development containers
if docker ps -a --format "table {{.Names}}" | grep -q "ai-safety-eval-dash.*_dev"; then
    echo "Development Environment:"
    check_container "ai-safety-eval-dash_backend_dev" "Backend (Dev)"
    
    check_container "ai-safety-eval-dash_postgres_dev" "PostgreSQL (Dev)"
    
    check_container "ai-safety-eval-dash_redis_dev" "Redis (Dev)"
    check_container "ai-safety-eval-dash_kafka_dev" "Kafka (Dev)"
    check_container "ai-safety-eval-dash_zookeeper_dev" "Zookeeper (Dev)"
    check_container "ai-safety-eval-dash_rabbitmq_dev" "RabbitMQ (Dev)"
    echo ""
fi

# Check production containers
if docker ps -a --format "table {{.Names}}" | grep -q "ai-safety-eval-dash_.*" | grep -v "_dev"; then
    echo "Production Environment:"
    check_container "ai-safety-eval-dash_backend" "Backend (Prod)"
    
    check_container "ai-safety-eval-dash_postgres" "PostgreSQL (Prod)"
    
    check_container "ai-safety-eval-dash_redis" "Redis (Prod)"
    check_container "ai-safety-eval-dash_kafka" "Kafka (Prod)"
    check_container "ai-safety-eval-dash_zookeeper" "Zookeeper (Prod)"
    check_container "ai-safety-eval-dash_rabbitmq" "RabbitMQ (Prod)"
    echo ""
fi

echo "🌐 Service Health Checks:"
echo "------------------------"

# Check service endpoints
check_service "Backend API" "8000" "/health"
check_service "Backend Docs" "8000" "/docs"


# PostgreSQL health check
echo -n "🔍 PostgreSQL: "
if docker exec ai-safety-eval-dash_postgres_dev pg_isready -U postgres > /dev/null 2>&1 || \
   docker exec ai-safety-eval-dash_postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi


# Redis health check
echo -n "🔍 Redis: "
if docker exec ai-safety-eval-dash_redis_dev redis-cli ping > /dev/null 2>&1 || \
   docker exec ai-safety-eval-dash_redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi

# RabbitMQ health check
echo -n "🔍 RabbitMQ: "
if curl -f -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✅ Healthy (Management UI available)"
else
    echo "❌ Unhealthy or not running"
fi

# Kafka health check
echo -n "🔍 Kafka: "
if docker exec ai-safety-eval-dash_kafka_dev kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1 || \
   docker exec ai-safety-eval-dash_kafka kafka-topics --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy or not running"
fi

echo ""
echo "📈 Resource Usage:"
echo "-----------------"

# Show Docker stats for running containers
if docker ps --format "table {{.Names}}" | grep -q "ai-safety-eval-dash"; then
    echo "Docker Container Stats:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker ps --filter "name=ai-safety-eval-dash" --format "{{.Names}}" | tr '\n' ' ') 2>/dev/null || true
else
    echo "No ai-safety-eval-dash containers running."
fi

echo ""
echo "🔗 Quick Links:"
echo "--------------"
echo "📋 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🩺 Health Check: http://localhost:8000/health"

echo "🗄️ pgAdmin: http://localhost:5050 (admin@ai-safety-eval-dash.local / admin)"

echo "🐰 RabbitMQ Management: http://localhost:15672 (guest/guest)"

# Show optional UIs if they're running
if docker ps --format "table {{.Names}}" | grep -q "kafka_ui"; then
    echo "📊 Kafka UI: http://localhost:8080"
fi

if docker ps --format "table {{.Names}}" | grep -q "redis_commander"; then
    echo "📊 Redis Commander: http://localhost:8081"
fi

echo ""
echo "💡 Tips:"
echo "   • Run './scripts/start.sh' to start services"
echo "   • Run './scripts/stop.sh' to stop services"
echo "   • Run 'docker-compose logs -f <service>' to view logs"
