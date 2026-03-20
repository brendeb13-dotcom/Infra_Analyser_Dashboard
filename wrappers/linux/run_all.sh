#!/bin/bash

echo "Running Storage Discovery..."
./discover_storage

echo "Running SAN Discovery..."
./discover_san

echo "Running Cluster Discovery..."
./discover_cluster

echo "All discovery completed!"