#!/bin/bash

echo "=========================================="
echo "Starting Distributed Key-Value Store"
echo "=========================================="
echo ""

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

echo ""
echo "Waiting for services to start..."
sleep 5

echo ""
echo "Checking service health..."
curl -s http://localhost:8000/health | python -m json.tool
echo ""
curl -s http://localhost:8001/health | python -m json.tool

echo ""
echo "=========================================="
echo "Cluster is ready!"
echo "=========================================="
echo ""
echo "Leader: http://localhost:8000"
echo "Followers: http://localhost:8001-8005"
echo ""
echo "Try these commands:"
echo "  Write: curl -X POST http://localhost:8000/write -H 'Content-Type: application/json' -d '{\"key\":\"test\",\"value\":\"hello\"}'"
echo "  Read:  curl http://localhost:8000/read?key=test"
echo ""
echo "Or run:"
echo "  python example_usage.py"
echo "  python integration_test.py"
echo "  python performance_analysis.py"
echo ""
